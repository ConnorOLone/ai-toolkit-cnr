---
name: maui-best-practices
description: Use when working in .NET MAUI codebases — writing/reviewing XAML, ViewModels, navigation, DI registrations, handlers, or diagnosing memory/performance issues. Covers .NET 8/9/10 MAUI patterns, CommunityToolkit.Mvvm, Shell navigation, compiled bindings, handler lifecycle, and common pitfalls.
disable-model-invocation: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# .NET MAUI Best Practices

A reference for writing idiomatic, performant, maintainable .NET MAUI code (.NET 8 / 9 / 10). Use this when touching MAUI code — views, view models, navigation, DI, handlers, platform interop, or performance/memory work.

## Quick decision table

| Question | Default answer |
|---|---|
| Which MVVM library? | `CommunityToolkit.Mvvm` — `[ObservableProperty]`, `[RelayCommand]`, `ObservableObject`. |
| Which DI container? | Built-in `Microsoft.Extensions.DependencyInjection` via `MauiAppBuilder.Services`. |
| Which navigation? | Shell with URI routing for most apps. `NavigationPage` only for simple linear stacks. |
| Messaging between VMs? | `WeakReferenceMessenger` (CommunityToolkit). **Never `MessagingCenter`** (deprecated, leaks). |
| Binding syntax? | Always `x:DataType` compiled bindings — 8–20× faster, catches errors at compile time. |
| List UI? | `CollectionView`. `ListView` is legacy. |
| Layout primitive? | `Grid` (with RowDefinitions/ColumnDefinitions) over nested `VerticalStackLayout`. |
| Platform code? | Partial classes in `Platforms/{OS}/` over `#if ANDROID` sprinkled through shared code. |
| Threading marshaling? | `MainThread.IsMainThread` check; `MainThread.InvokeOnMainThreadAsync` when awaiting. |
| Custom renderers? | Use **handlers** with `Mapper.AppendToMapping()`. Renderers are compatibility-only. |

## MVVM with CommunityToolkit.Mvvm

```csharp
public partial class OrderViewModel : ObservableObject
{
    [ObservableProperty] private string? customerName;
    [ObservableProperty] private bool isBusy;

    [RelayCommand(CanExecute = nameof(CanSave))]
    private async Task SaveAsync()
    {
        IsBusy = true;
        try { await _repo.SaveAsync(); }
        finally { IsBusy = false; }
    }

    private bool CanSave() => !IsBusy && !string.IsNullOrWhiteSpace(CustomerName);
}
```

Rules:
- `partial class` required — source generators emit the other half.
- Prefer `[ObservableProperty]` over manual `SetProperty` boilerplate.
- Keep ViewModels free of MAUI UI types (`Page`, `Shell`, `VisualElement`). Depend on abstractions (`INavigationService`, `IDialogService`) so VMs remain testable in a plain `net10.0` library.
- Async commands: use `[RelayCommand]` on `async Task` methods; the generator produces `IAsyncRelayCommand` with built-in `IsRunning` guard.

## Dependency Injection

```csharp
// MauiProgram.cs
builder.Services
    .AddSingleton<IAppSettings, AppSettings>()
    .AddSingleton<IDatabase, Database>()
    .AddTransient<OrdersViewModel>()
    .AddTransient<OrdersPage>();
```

Lifetimes:
- **Singleton** — stateless services: HTTP clients, logging, settings, SQLite connection wrapper, navigation service.
- **Transient** — ViewModels and Pages. Avoids stale state on re-navigation. Registering VMs as Singleton is a common bug.
- **Scoped** — rarely useful in MAUI; there is no request scope.

Resolve via constructor injection. Avoid service-locator calls (`Handler.MauiContext.Services.GetService<T>()`) except at root composition.

## Navigation — Shell

Register routes once, navigate by URI:

```csharp
Routing.RegisterRoute(nameof(OrderDetailsPage), typeof(OrderDetailsPage));

// Navigate with strongly typed params
await Shell.Current.GoToAsync(nameof(OrderDetailsPage),
    new Dictionary<string, object> { ["Order"] = selectedOrder });
```

Receive params:

```csharp
public partial class OrderDetailsViewModel : ObservableObject, IQueryAttributable
{
    public void ApplyQueryAttributes(IDictionary<string, object> query)
    {
        if (query.TryGetValue("Order", out var o) && o is Order order)
            Order = order;
    }
}
```

- Prefer `IQueryAttributable` over `[QueryProperty]` for complex objects.
- `GoToAsync("..")` pops one level; `"///route"` resets the stack.
- Don't call `Shell.Current` from ViewModels — wrap in `INavigationService`.

## Bindings

```xml
<ContentPage xmlns:vm="clr-namespace:App.ViewModels"
             x:DataType="vm:OrdersViewModel">
    <CollectionView ItemsSource="{Binding Orders}">
        <CollectionView.ItemTemplate>
            <DataTemplate x:DataType="vm:OrderItemViewModel">
                <Label Text="{Binding CustomerName}" />
            </DataTemplate>
        </CollectionView.ItemTemplate>
    </CollectionView>
</ContentPage>
```

- Set `x:DataType` on every `ContentPage` and every `DataTemplate` — compiled bindings are 8–20× faster than reflection bindings and fail at build time when a property is renamed.
- In .NET 9+, set `<MauiEnableXamlCBindingWithSourceCompilation>true</MauiEnableXamlCBindingWithSourceCompilation>` in the csproj to extend compiled bindings to `Source`-based bindings.
- Opt out locally with `x:DataType="{x:Null}"` when binding against dynamic data.

## Memory leaks — the #1 MAUI issue class

MAUI does **not** automatically disconnect handlers when pages are popped. Symptoms: ViewModels and Pages are never GC'd; memory grows each navigation.

**Checklist when diagnosing a leak:**

1. **Handler disconnection.** For custom controls, override `DisconnectHandler`:
   ```csharp
   protected override void DisconnectHandler(PlatformView platformView)
   {
       platformView.SomeEvent -= OnSomeEvent;
       base.DisconnectHandler(platformView);
   }
   ```
   .NET 9 added `HandlerDisconnectPolicy` (`Automatic` / `Manual`) — prefer `Automatic` where supported.

2. **Event subscriptions.** Any `+=` on a longer-lived object (static events, `Connectivity.ConnectivityChanged`, singleton services) pins the subscriber. Unsubscribe in `OnDisappearing`/`Dispose`, or use `WeakEventManager` / `WeakReferenceMessenger`.

3. **No `MessagingCenter`.** It's deprecated and leaks. Replace with `WeakReferenceMessenger.Default.Send/Register`.

4. **No captured `this` in long-lived lambdas** attached to singletons.

5. **Profile heap** with `dotnet-gcdump collect -p <pid>` and compare before/after navigation cycles.

## Performance

- **Release builds**: enable AOT + trimming.
  ```xml
  <RunAOTCompilation>true</RunAOTCompilation>
  <AndroidEnableProfiledAot>true</AndroidEnableProfiledAot>
  <PublishTrimmed>true</PublishTrimmed>
  <TrimMode>full</TrimMode>
  ```
  iOS in .NET 9+ supports NativeAOT (~2.5× smaller app, ~2× faster startup).
- **Never ship** `<UseInterpreter>true</UseInterpreter>` — debug only.
- **Flatten visual trees.** Each nested `StackLayout` adds a measure/arrange pass. Prefer `Grid`. Use `CompressedLayout.IsHeadless="true"` on wrapper layouts.
- **Images**: set explicit `WidthRequest`/`HeightRequest`; use `MauiImage` build-time resizing per DPI bucket.
- **CollectionView**: set `ItemsUpdatingScrollMode`; avoid nested `CollectionView`s; use `x:DataType` in `DataTemplate`.

## Threading

- **Rule:** don't use `ConfigureAwait(false)` in UI-layer code (ViewModels, code-behind). It drops you off the UI thread, causing binding updates to fail or crash. Do use it in `Core`/library code.
- **Rule:** no `async void` except for actual event handlers — exceptions are unobservable.
- **Marshaling:**
  ```csharp
  if (!MainThread.IsMainThread)
      await MainThread.InvokeOnMainThreadAsync(UpdateUi);
  else
      UpdateUi();
  ```
  Don't reflexively wrap everything in `MainThread.BeginInvokeOnMainThread` — causes jank.

## Platform-specific code

Prefer partial classes:

```
Services/IBarcode.cs                  // interface
Services/Barcode.cs                   // partial class, shared
Platforms/Android/Services/Barcode.cs // partial implementation
Platforms/iOS/Services/Barcode.cs
```

Register in each platform's DI wiring or use `Services.AddSingleton<IBarcode, Barcode>()` in shared code when the partial provides a single type.

Use `#if ANDROID` only for one-liners; scale to partial classes beyond that.

## Lifecycle gotchas

- `OnAppearing` fires **every** time the page appears (modal dismissal, tab switch, nav back). One-shot init needs an `_isInitialized` flag, or do it in the constructor / `ApplyQueryAttributes`.
- Android hardware back on Shell: use `Shell.BackButtonBehavior`, not `OnBackButtonPressed`.
- iOS safe area: `On<iOS>().SetUseSafeArea(true)` per page if needed; default shifted across versions.

## Configuration

Embed `appsettings.json` as `MauiAsset` and load via `Microsoft.Extensions.Configuration`:

```csharp
using var stream = await FileSystem.OpenAppPackageFileAsync("appsettings.json");
var config = new ConfigurationBuilder().AddJsonStream(stream).Build();
builder.Services.Configure<AppOptions>(config.GetSection("App"));
```

**Never ship secrets in the embedded JSON.** Use `SecureStorage.Default` for runtime secrets, CI secret injection for build-time values.

## Logging

```csharp
builder.Logging.AddDebug();
builder.Services.AddSingleton<ILogger>(sp =>
    sp.GetRequiredService<ILoggerFactory>().CreateLogger("App"));
```

For production add Serilog (`UseSerilog`) with file sink, or `Microsoft.Extensions.Logging.ApplicationInsights`. App Center Analytics retires **June 30, 2026** — Sentry has a first-class .NET MAUI SDK for crashes/perf; Firebase Crashlytics is the free alternative.

## Testing

- Put ViewModels and services in `net10.0` (not `net10.0-android`) class libraries so tests run without the MAUI workload.
- Stack: xUnit + NSubstitute + FluentAssertions + coverlet.collector.
- UI tests: Appium + `Plugin.Maui.UITestHelpers` (Xamarin.UITest is retired).
- XAML Hot Reload is default-on in VS 2022 and VS Code.

## Xamarin.Forms → MAUI migration cheat sheet

| Xamarin.Forms | .NET MAUI |
|---|---|
| Custom Renderer | Handler (`Mapper.AppendToMapping`) |
| `MessagingCenter` | `WeakReferenceMessenger` |
| `Device.BeginInvokeOnMainThread` | `MainThread.BeginInvokeOnMainThread` |
| `App.xaml.cs` startup | `MauiProgram.CreateMauiApp` |
| `DependencyService` | `Microsoft.Extensions.DependencyInjection` |
| `Xamarin.Essentials` | `Microsoft.Maui.Essentials` (built in) |

## SQLite pitfalls

- `SQLiteAsyncConnection` serializes through a single connection lock — `Task.WhenAll` over queries buys nothing and can deadlock if mixed with sync calls.
- Don't share a raw `SQLiteConnection` across threads — use the async wrapper.
- Transactions via `RunInTransactionAsync` provide atomicity; Unit-of-Work is usually overkill on mobile.

## What this skill is NOT

- Not a tutorial. Assume the reader can write C# and basic XAML.
- Not exhaustive on every control. Covers the patterns that prevent the most bugs.
- Release notes may have moved. For .NET 10 specifics, verify against `learn.microsoft.com/dotnet/maui/whats-new/dotnet-10`.

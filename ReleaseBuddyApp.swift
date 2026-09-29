import SwiftUI

@main
struct ReleaseBuddyApp: App {
    @StateObject private var store = PipelineStore()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(store)
                .frame(minWidth: 860, minHeight: 600)
        }
        .windowStyle(.titleBar)
        .commands {
            CommandGroup(after: .appInfo) {
                Button("Reset All Progress") { store.resetProgress() }
                    .keyboardShortcut("r", modifiers: [.command, .shift])
            }
        }
    }
}

struct ContentView: View {
    @EnvironmentObject var store: PipelineStore
    @State private var selection: String? = "pipeline"

    var body: some View {
        NavigationSplitView {
            List(selection: $selection) {
                Label("Release Pipeline", systemImage: "paperplane.fill").tag("pipeline")
                Label("API Key Setup", systemImage: "key.fill").tag("setup")
                Label("Settings", systemImage: "gearshape.fill").tag("settings")
            }
            .navigationTitle("ReleaseBuddy")
        } detail: {
            switch selection {
            case "setup": SetupView()
            case "settings": SettingsView()
            default: PipelineView()
            }
        }
        .environmentObject(store)
    }
}

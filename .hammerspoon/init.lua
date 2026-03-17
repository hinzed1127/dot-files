hs.loadSpoon("AppWindowSwitcher")
    -- :setLogLevel("debug") -- change to "debug" for troubleshooting
    :bindHotkeys({
        ["com.mitchellh.ghostty"]     = {{"cmd", "ctrl", "shift", "alt"}, "g"}, -- Ghostty
        [{"company.thebrowser.Browser",
          "com.google.Chrome"}]       = {{"cmd", "ctrl", "shift", "alt"}, "b"}, -- Browsers
        [{"com.qobuz.desktop",
          "com.apple.Music"}]       = {{"cmd", "ctrl", "shift", "alt"}, "m"}, -- Music
        ["com.tinyspeck.slackmacgap"] = {{"cmd", "ctrl", "shift", "alt"}, "s"}, -- Slack
    })

-- spoon.SpoonInstall:andUse("AppLauncher", {
hs.loadSpoon("AppLauncher")
  :bindHotkeys({
    s = "Slack",
  })

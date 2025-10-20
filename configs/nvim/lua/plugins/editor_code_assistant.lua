-- Editor code assistant
-- Integrates AI into neovim
return {
  "editor-code-assistant/eca-nvim",
  dependencies = {
    "MunifTanjim/nui.nvim",   -- Required: UI framework
    "nvim-lua/plenary.nvim",  -- Optional: Enhanced async operations
  },
  keys = {
    { "<leader>ac", "<cmd>EcaChat<cr>", desc = "Open ECA chat" },
    { "<leader>af", "<cmd>EcaFocus<cr>", desc = "Focus ECA sidebar" },
    { "<leader>at", "<cmd>EcaToggle<cr>", desc = "Toggle ECA sidebar" },
  },
  opts = {
    debug = true,
    server_path = "",
    behavior = {
      auto_set_keymaps = false,
      auto_focus_sidebar = false,
    },
  }
}

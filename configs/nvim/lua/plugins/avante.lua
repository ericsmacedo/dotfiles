return {
  "yetone/avante.nvim",
  dependencies = {
    "nvim-tree/nvim-web-devicons",
    "stevearc/dressing.nvim",
    "nvim-lua/plenary.nvim",
    "MunifTanjim/nui.nvim",
    {
      "MeanderingProgrammer/render-markdown.nvim",
      opts = { file_types = { "markdown", "Avante" } },
      ft = { "markdown", "Avante" },
    },
  },
  build = "make",
  opts = {
    provider = "copilot",
    mode = "legacy",

    behaviour = {
      auto_suggestions = false, -- Experimental stage
      auto_set_highlight_group = true,
      auto_set_keymaps = true,
      auto_apply_diff_after_generation = false,
      support_paste_from_clipboard = false,
      minimize_diff = true, -- Whether to remove unchanged lines when applying a code block
      enable_token_counting = true, -- Whether to enable token counting. Default to true.
      auto_add_current_file = true, -- Whether to automatically add the current file when opening a new chat. Default to true.
      auto_approve_tool_permissions = false, -- Default: auto-approve all tools (no prompts)
      -- Examples:
      -- auto_approve_tool_permissions = false,                -- Show permission prompts for all tools
      -- auto_approve_tool_permissions = {"bash", "str_replace"}, -- Auto-approve specific tools only
      ---@type "popup" | "inline_buttons"
      confirmation_ui_style = "inline_buttons",
      --- Whether to automatically open files and navigate to lines when ACP agent makes edits
      ---@type boolean
      acp_follow_agent_locations = true,
    },
  },
}

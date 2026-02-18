
return {
  "github/copilot.vim",
  cmd = "Copilot",
  event = "BufWinEnter",
  init = function()
    -- don't install Copilot's default keymaps
    vim.g.copilot_no_maps = true
  end,
  config = function()
    -- Turn on Copilot's LSP backend without its inline suggestion UI
    vim.api.nvim_create_autocmd({ "FileType", "BufUnload" }, {
      group = vim.api.nvim_create_augroup("github_copilot", { clear = true }),
      callback = function(args)
        vim.fn["copilot#On" .. args.event]()
      end,
    })
    vim.fn["copilot#OnFileType"]()
  end,
}

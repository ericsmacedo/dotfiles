return {
  "github/copilot.vim",
  cmd = "Copilot",
  event = "BufWinEnter",
  init = function()
    -- blink-copilot displays suggestions through blink.cmp.
    vim.g.copilot_no_maps = true
  end,
  config = function()
    local group = vim.api.nvim_create_augroup("github_copilot", { clear = true })
    vim.api.nvim_create_autocmd({ "FileType", "BufUnload" }, {
      group = group,
      callback = function(args)
        vim.fn["copilot#On" .. args.event]()
      end,
    })
    vim.fn["copilot#OnFileType"]()
  end,
}

-- nvim-spectre integration for Neovim
-- https://github.com/nvim-pack/nvim-spectre

return {
    "nvim-pack/nvim-spectre",
    event = "VeryLazy",
    config = function()
        require("spectre").setup {}
    end,
    keys = {
        {
            "<leader>S",
            function()
                require("spectre").open()
            end,
            desc = "Spectre: Search and Replace",
        },
    },
}

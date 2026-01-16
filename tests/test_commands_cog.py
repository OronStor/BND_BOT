import pytest
from unittest.mock import MagicMock, AsyncMock, patch

class TestFeetCommand:
    @pytest.mark.asyncio
    async def test_feet(self):
        ctx = MagicMock()
        ctx.author.mention = "<@123>"
        ctx.send = AsyncMock()
        
        from cogs.commands import CommandsCog
        cog = CommandsCog(bot=None)
        
        await cog.feet.callback(cog,ctx)
        ctx.send.assert_called_once_with("Hey, <@123>... Can I smell your feet??")
        
class TestSilverCommand:
    @patch("cogs.commands.discord.File")
    @pytest.mark.asyncio
    async def test_silver_empty_folder(self , mock_file_class):
        from cogs.commands import CommandsCog
        cog = CommandsCog(bot=None)
        cog.silver_images = []
        
        ctx = MagicMock()
        ctx.send = AsyncMock()
        
        await cog.silver.callback(cog,ctx)
        ctx.send.assert_called_once_with("No images found in the silvername folder.")
        
    @patch("cogs.commands.discord.File")
    @pytest.mark.asyncio
    async def test_silver_single_image(self , mock_file_class):
        from cogs.commands import CommandsCog
        cog = CommandsCog(bot=None)
        cog.silver_images = ["image1.jpg"]
        
        ctx = MagicMock()
        ctx.send = AsyncMock()
        
        await cog.silver.callback(cog,ctx)
        
        ctx.send.assert_called_once_with(file=mock_file_class.return_value)
        
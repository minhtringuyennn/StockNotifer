<<<<<<< HEAD
import discord, asyncio, requests, random, configparser, os
from discord.ext import commands
from discord.commands import slash_command, Option
from PIL import Image, ImageDraw, ImageFont

import stock_modules.fetch as fetch
import stock_modules.utils as utils
import stock_modules.figure as figure
import stock_modules.indicate as indicate
import commands.constants as constants

class Price(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        read_config = configparser.ConfigParser()
        path = os.path.join(os.path.abspath(__file__+"/../../"),"config", "config.ini")
        read_config.read(path)
        self.__TIMEOUT = int(read_config.get("config", "TIME_OUT"))
        
    @discord.slash_command(
        name='price',
        description='Check symbols price.'
    )
    async def getStockPrice(self, ctx, *, symbols):
        # symbols = str(symbols)
        symbols_list = symbols.replace(' ','').split(",")

        # Check symbols contains list of stocks or not
        if not isinstance(symbols_list, list):
            symbols = [symbols_list]
        else:
            symbols = symbols_list
        # print(symbols)
        for symbol in symbols:
            await self.getEachStockPrice(ctx, symbol)
        
    async def getEachStockPrice(self, ctx, symbol):
        data = fetch.fetchCurrentPrice(symbol.upper())

        if (data != None):
            mess = ""
            
            changeRate = (1.0 - (float(data['PriceBasic']) / float(data['PriceCurrent']))) * 100.0
            changeRate = round(changeRate, 2)
            
            changePrice = float(data['PriceCurrent']) - float(data['PriceBasic'])
            # changePrice = round(changePrice, 2)
            
            # Currently for HOSE market only
            if changeRate >= 6.9:
                mess = random.choice(constants.MESS_CE)
                embed = discord.Embed(color=constants.COLOR_CE)
            elif changeRate <= -6.9:
                mess = random.choice(constants.MESS_FL)
                embed = discord.Embed(color=constants.COLOR_FL)
            elif changeRate > 0.0:
                mess = random.choice(constants.MESS_UP)
                embed = discord.Embed(color=constants.COLOR_UP)
            elif changeRate < 0.0:
                mess = random.choice(constants.MESS_DOWN)
                embed = discord.Embed(color=constants.COLOR_DOWN)
            elif changeRate == 0.0:
                mess = random.choice(constants.MESS_TC)
                embed = discord.Embed(color=constants.COLOR_TC)
                
            price_str = str(data["PriceCurrent"])
            mess = mess.replace("#code#",symbol.upper()).replace("#price#", price_str)
            
            embed.set_author(name=f'Giá của {symbol.upper()} tại {utils.get_current_time(data["Date"])}:')
            embed.add_field(name='Giá: ', value=f'{utils.format_value(data["PriceCurrent"])}', inline=True)
            embed.add_field(name='% thay đổi với hôm trước: ', value=f'{changeRate}%', inline=True)
            embed.add_field(name='Giá thay đổi với hôm trước: ', value=f'{utils.format_value(changePrice)}', inline=True)
            
            embed.add_field(name='KL Mua chủ động: ', value=f'{utils.format_value(data["TotalActiveBuyVolume"])}', inline=True)
            embed.add_field(name='KL Bán chủ động: ', value=f'{utils.format_value(data["TotalActiveSellVolume"])}', inline=True)
            embed.add_field(name='Tổng KLGD: ', value=f'{utils.format_value(data["TotalVolume"])}', inline=True)
            
            embed.add_field(name='KL nước ngoài Mua: ', value=f'{utils.format_value(data["BuyForeignQuantity"])}', inline=True)
            embed.add_field(name='KL nước ngoài Bán: ', value=f'{utils.format_value(data["SellForeignQuantity"])}', inline=True)        
        
            await ctx.respond(mess, delete_after=self.__TIMEOUT)
            await ctx.send(embed=embed, delete_after=self.__TIMEOUT)
        else:
            mess = "Mã cổ phiếu không hợp lệ."
            await ctx.respond(mess, delete_after=self.__TIMEOUT)
            
    @discord.slash_command(
        name='briefstats',
        description='Check symbol brief stats.'
    )
    async def getStockBrief(self, ctx, *, symbols):
        # symbols = str(symbols)
        symbols_list = symbols.replace(' ','').split(",")

        # Check symbols contains list of stocks or not
        if not isinstance(symbols_list, list):
            symbols = [symbols_list]
        else:
            symbols = symbols_list
        # print(symbols)
        for symbol in symbols:
            await self.getEachStockBrief(ctx, symbol)

    async def getEachStockBrief(self, ctx, symbol):
        data = fetch.fetchFianancialInfo(symbol.upper())
        # print(data)
        if (data != None):
            embed = discord.Embed()
            embed.set_author(name=f'Thông tin của doanh nghiệp {symbol}:')
            embed.add_field(name='Giá trị EPS: ', value=f'{utils.format_value(data["BasicEPS"])}', inline=True)
            embed.add_field(name='Giá trị P/E: ', value=f'{utils.format_value(data["BasicPE"])}', inline=True)
            embed.add_field(name='Giá trị P/B: ', value=f'{utils.format_value(data["BookValuePerShare"])}', inline=True)
            embed.add_field(name='Giá trị ROA: ', value=f'{utils.format_percent(data["ROA"])}', inline=True)
            embed.add_field(name='Giá trị ROE: ', value=f'{utils.format_percent(data["ROE"])}', inline=True)
            embed.add_field(name='Giá trị ROIC: ', value=f'{data["ROIC"]}', inline=True)
            embed.add_field(name='Giá trị EBIT: ', value=f'{utils.format_value(data["EBIT"])}', inline=True)
            embed.add_field(name='Giá trị EBITDA: ', value=f'{utils.format_value(data["EBITDA"])}', inline=True)
            
            await ctx.respond(f"Thông tin của doanh nghiệp: {symbol.upper()} đến ngày {utils.get_today_date()}", delete_after=self.__TIMEOUT)
            await ctx.send(embed=embed, delete_after=self.__TIMEOUT)
        else:
            mess = "Mã cổ phiếu không hợp lệ."
            await ctx.respond(mess, delete_after=self.__TIMEOUT)
            
    @slash_command(
        name='chart',
        description='Check symbol chart.'
    )
    async def getStockChart(self, ctx, *, symbols):
        # symbols = str(symbols)
        symbols_list = symbols.replace(' ','').split(",")

        # Check symbols contains list of stocks or not
        if not isinstance(symbols_list, list):
            symbols = [symbols_list]
        else:
            symbols = symbols_list
        # print(symbols)
        for symbol in symbols:
            await self.getEachChart(ctx, symbol)

    async def getEachChart(self, ctx, symbol):
        len = 30
        symbol = symbol.strip().upper()
        start_date = utils.get_last_year_date()
        end_date = utils.get_today_date()
        loader = fetch.DataLoader(symbol, start_date, end_date)
        data = loader.fetchPrice()
        figure.drawFigure(data ,symbol, length=len)
        figure.img.seek(0)
        await ctx.respond(f"Biểu đồ của {symbol} trong {len} ngày gần đây!", delete_after=self.__TIMEOUT)
        await ctx.send(file=discord.File(figure.img, filename=f'{symbol}.png'), delete_after=self.__TIMEOUT)
=======
import discord, asyncio, requests, random, configparser, os
from discord.ext import commands
from discord.commands import slash_command, Option
from PIL import Image, ImageDraw, ImageFont

import stock_modules.fetch as fetch
import stock_modules.utils as utils
import stock_modules.figure as figure
import stock_modules.indicate as indicate
import commands.constants as constants

class Price(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        read_config = configparser.ConfigParser()
        path = os.path.join(os.path.abspath(__file__+"/../../"),"config", "config.ini")
        read_config.read(path)
        self.__TIMEOUT = int(read_config.get("config", "TIME_OUT"))
        
    @discord.slash_command(
        name='price',
        description='Check symbols price.'
    )
    async def getStockPrice(self, ctx, *, symbols):
        # symbols = str(symbols)
        symbols_list = symbols.replace(' ','').split(",")

        # Check symbols contains list of stocks or not
        if not isinstance(symbols_list, list):
            symbols = [symbols_list]
        else:
            symbols = symbols_list
        # print(symbols)
        for symbol in symbols:
            await self.getEachStockPrice(ctx, symbol)
        
    async def getEachStockPrice(self, ctx, symbol):
        data = fetch.fetchCurrentPrice(symbol.upper())

        if (data != None):
            mess = ""
            
            changeRate = (1.0 - (float(data['PriceBasic']) / float(data['PriceCurrent']))) * 100.0
            changeRate = round(changeRate, 2)
            
            changePrice = float(data['PriceCurrent']) - float(data['PriceBasic'])
            # changePrice = round(changePrice, 2)
            
            # Currently for HOSE market only
            if changeRate >= 6.9:
                mess = random.choice(constants.MESS_CE)
                embed = discord.Embed(color=constants.COLOR_CE)
            elif changeRate <= -6.9:
                mess = random.choice(constants.MESS_FL)
                embed = discord.Embed(color=constants.COLOR_FL)
            elif changeRate > 0.0:
                mess = random.choice(constants.MESS_UP)
                embed = discord.Embed(color=constants.COLOR_UP)
            elif changeRate < 0.0:
                mess = random.choice(constants.MESS_DOWN)
                embed = discord.Embed(color=constants.COLOR_DOWN)
            elif changeRate == 0.0:
                mess = random.choice(constants.MESS_TC)
                embed = discord.Embed(color=constants.COLOR_TC)
                
            price_str = str(data["PriceCurrent"])
            mess = mess.replace("#code#",symbol.upper()).replace("#price#", price_str)
            
            embed.set_author(name=f'Giá của {symbol.upper()} tại {utils.get_current_time(data["Date"])}:')
            embed.add_field(name='Giá: ', value=f'{utils.format_value(data["PriceCurrent"])}', inline=True)
            embed.add_field(name='% thay đổi với hôm trước: ', value=f'{changeRate}%', inline=True)
            embed.add_field(name='Giá thay đổi với hôm trước: ', value=f'{utils.format_value(changePrice)}', inline=True)
            
            embed.add_field(name='KL Mua chủ động: ', value=f'{utils.format_value(data["TotalActiveBuyVolume"])}', inline=True)
            embed.add_field(name='KL Bán chủ động: ', value=f'{utils.format_value(data["TotalActiveSellVolume"])}', inline=True)
            embed.add_field(name='Tổng KLGD: ', value=f'{utils.format_value(data["TotalVolume"])}', inline=True)
            
            embed.add_field(name='KL nước ngoài Mua: ', value=f'{utils.format_value(data["BuyForeignQuantity"])}', inline=True)
            embed.add_field(name='KL nước ngoài Bán: ', value=f'{utils.format_value(data["SellForeignQuantity"])}', inline=True)        
        
            await ctx.respond(mess, delete_after=self.__TIMEOUT)
            await ctx.send(embed=embed, delete_after=self.__TIMEOUT)
        else:
            mess = "Mã cổ phiếu không hợp lệ."
            await ctx.respond(mess, delete_after=self.__TIMEOUT)
            
    @discord.slash_command(
        name='briefstats',
        description='Check symbol brief stats.'
    )
    async def getStockBrief(self, ctx, *, symbols):
        # symbols = str(symbols)
        symbols_list = symbols.replace(' ','').split(",")

        # Check symbols contains list of stocks or not
        if not isinstance(symbols_list, list):
            symbols = [symbols_list]
        else:
            symbols = symbols_list
        # print(symbols)
        for symbol in symbols:
            await self.getEachStockBrief(ctx, symbol)

    async def getEachStockBrief(self, ctx, symbol):
        data = fetch.fetchFianancialInfo(symbol.upper())
        # print(data)
        if (data != None):
            embed = discord.Embed()
            embed.set_author(name=f'Thông tin của doanh nghiệp {symbol}:')
            embed.add_field(name='Giá trị EPS: ', value=f'{utils.format_value(data["BasicEPS"])}', inline=True)
            embed.add_field(name='Giá trị P/E: ', value=f'{utils.format_value(data["BasicPE"])}', inline=True)
            embed.add_field(name='Giá trị P/B: ', value=f'{utils.format_value(data["BookValuePerShare"])}', inline=True)
            embed.add_field(name='Giá trị ROA: ', value=f'{utils.format_percent(data["ROA"])}', inline=True)
            embed.add_field(name='Giá trị ROE: ', value=f'{utils.format_percent(data["ROE"])}', inline=True)
            embed.add_field(name='Giá trị ROIC: ', value=f'{data["ROIC"]}', inline=True)
            embed.add_field(name='Giá trị EBIT: ', value=f'{utils.format_value(data["EBIT"])}', inline=True)
            embed.add_field(name='Giá trị EBITDA: ', value=f'{utils.format_value(data["EBITDA"])}', inline=True)
            
            await ctx.respond(f"Thông tin của doanh nghiệp: {symbol.upper()} đến ngày {utils.get_today_date()}", delete_after=self.__TIMEOUT)
            await ctx.send(embed=embed, delete_after=self.__TIMEOUT)
        else:
            mess = "Mã cổ phiếu không hợp lệ."
            await ctx.respond(mess, delete_after=self.__TIMEOUT)
            
    @slash_command(
        name='chart',
        description='Check symbol chart.'
    )
    async def getStockChart(self, ctx, *, symbols):
        # symbols = str(symbols)
        symbols_list = symbols.replace(' ','').split(",")

        # Check symbols contains list of stocks or not
        if not isinstance(symbols_list, list):
            symbols = [symbols_list]
        else:
            symbols = symbols_list
        # print(symbols)
        for symbol in symbols:
            await self.getEachChart(ctx, symbol)

    async def getEachChart(self, ctx, symbol):
        len = 30
        symbol = symbol.strip().upper()
        start_date = utils.get_last_year_date()
        end_date = utils.get_today_date()
        loader = fetch.DataLoader(symbol, start_date, end_date)
        data = loader.fetchPrice()
        figure.drawFigure(data ,symbol, length=len)
        figure.img.seek(0)
        await ctx.respond(f"Biểu đồ của {symbol} trong {len} ngày gần đây!", delete_after=self.__TIMEOUT)
        await ctx.send(file=discord.File(figure.img, filename=f'{symbol}.png'), delete_after=self.__TIMEOUT)
>>>>>>> b6132805818c3f49cacf84d3438012040128a34f
        figure.img.seek(0)
import discord
import os
import asyncio
import ffmpeg
import random
import yt_dlp as youtube_dl
from dotenv import load_dotenv
from discord.ext import commands,tasks

load_dotenv()

# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='/',intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': './downloads/%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
}

ffmpeg_options = {'options': '-vn'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.7):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

# Remove o comando de ajuda padrão, eu decidi criar o meu próprio
bot.remove_command('help')

@bot.event
async def on_ready():
    print("Bot pronto.")

@bot.command(name='join', help='Chama o bot para o chat de voz')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} não está conectado à um canal de voz".format(ctx.message.author.name))
        return
    else:
        voice_client = ctx.message.guild.voice_client
        if not voice_client:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("O bot já está conectado ao canal de voz.")

@bot.command(name='leave', help='Para expulsar o bot')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("O bot não está conectado à um canal de voz.")

@bot.command(name='play', help='Toca a musica especificada pela url em seguida')
async def play(ctx,url):
    try :
        # Conecta o bot se não estiver conectado
        await join(ctx)

        # Se outra pessoa pedir para tocar, ele vai imediatamente
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()

        server = ctx.message.guild
        voice_channel = server.voice_client

        filename = await YTDLSource.from_url(url, loop=bot.loop)
        
        #windows: "C:\\ffmpeg\\bin\\ffmpeg.exe"                
        #voice_channel.play(discord.FFmpegPCMAudio(executable="caminho", source=filename))
        
        voice_channel.play(discord.FFmpegPCMAudio(filename, **ffmpeg_options))
        await ctx.send('Tocando a música selecionada')

    except Exception as err:
        print(err)
        return

@bot.command(name='pause', help='Pausa a música atual')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("O bot não está tocando no momento.")
    
@bot.command(name='resume', help='Continua com a música')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("O bot não tem nada para tocar")

@bot.command(name='stop', help='Para a música')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("O bot não está tocando no momento.")

@bot.command(name='cavalo', help='CAVALO')
async def cavalo(ctx):
    try :
        await join(ctx)

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()

        url = 'https://www.youtube.com/watch?v=1xzGPPxKgJM'
        server = ctx.message.guild
        voice_channel = server.voice_client

        filename = await YTDLSource.from_url(url, loop=bot.loop)
        voice_channel.play(discord.FFmpegPCMAudio(filename, **ffmpeg_options))

        await ctx.send('**CAVALO**')
    except Exception as err:
        print(err)
        return

@bot.command(name='rapaiz', help='RAPAAAAAIZZZZZZ')
async def cavalo(ctx):
    try :
        await join(ctx)
        
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()

        url = 'https://www.youtube.com/watch?v=HXYNW0ft5o4'
        server = ctx.message.guild
        voice_channel = server.voice_client

        filename = await YTDLSource.from_url(url, loop=bot.loop)            
        voice_channel.play(discord.FFmpegPCMAudio(filename, **ffmpeg_options))

        await ctx.send('**RAPAAAAAIZZZZZZ**')
    except Exception as err:
        print(err)
        return

@bot.command(name='apresentar', help='Apresenta dados sobre o servidor')
async def apresentar(ctx):
        msgs = ['O bot está on!', 'O Pai tá on!', 'Alguém me chamou?!', 'Opa eae!']
        gifs = ['hunters', 'dancing_dante','all_good_bb']
        var = str(random.choice(msgs))+'\n\nCriador(a): {}\nServidor: {}\nQuantia de membros: {}\n'.format(ctx.guild.owner, ctx.guild.name,ctx.guild.member_count)
        file = discord.File('./gifs/'+str(random.choice(gifs)+'.gif'), filename='image.gif')

        embed = discord.Embed()
        embed.color = 2123412
        embed.title = 'Apresentando informações do server:'
        embed.set_thumbnail(url='attachment://image.gif')
        embed.description = var
        
        await ctx.send(file=file, embed=embed)

@bot.command(name='help', help='Esta função exibe os comandos do bot')
async def help(ctx):
    try:
        
        var="/help - Esta função exibe os comandos do bot\n"
        var+="/join - Chama o bot para o chat de voz\n"
        var+="/play <url> - Toca a musica especificada pela url em seguida\n"
        var+="/leave - Abandona o chat de voz\n"
        var+="/pause - Pausa a música atual\n"
        var+="/resume - Continua com a música\n"
        var+="/stop - Para a música\n"
        var+="/apresentar - Apresenta dados sobre o servidor\n"
        var+="\n"
        
        embed = discord.Embed()
        embed.color = 2123412
        embed.title = 'Lista de Comandos:'
        embed.description = var
        embed.add_field(name='Em desenvolvimento:', value='/surv_build - Apresenta uma build de DBD para o survivor\n', inline=False)
        

        await ctx.send(embed=embed)
    except Exception as err:
        print(err)
        return
    

if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)

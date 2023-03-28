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

titulo_video = ''

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.7):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False,ctx):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)

        titulo_video = str(data['title'])
        embed = discord.Embed()
        embed.color = 2123412
        embed.description = "**Título:  **"+titulo_video

        await ctx.send(embed=embed)
        
        return filename

# Remove o comando de ajuda padrão, eu decidi criar o meu próprio
bot.remove_command('help')

@bot.event
async def on_ready():
    print("Bot pronto.")

@bot.command(name='join', help='Chama o bot para o chat de voz')
async def join(ctx):
    if not ctx.message.author.voice:
        embed = mensagem("","","","{} não está conectado à um canal de voz".format(ctx.message.author.name))
        await ctx.send(embed=embed)
        return
    else:
        voice_client = ctx.message.guild.voice_client
        if not voice_client:
            embed = mensagem("","","","Conectando ao canal de voz.")
            await ctx.send(embed=embed)
            
            channel = ctx.message.author.voice.channel
            await channel.connect()
        else:
            embed = mensagem("","","","O bot já está conectado ao canal de voz.")
            await ctx.send(embed=embed)

@bot.command(name='leave', help='Para expulsar o bot')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        embed = mensagem("","","","Desconectando do canal de voz.")
        await ctx.send(embed=embed)
        await voice_client.disconnect()
    else:
        embed = mensagem("","","","O bot não está conectado à um canal de voz.")
        await ctx.send(embed=embed)

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

        filename = await YTDLSource.from_url(url, loop=bot.loop,ctx=ctx)
        
        #windows: "C:\\ffmpeg\\bin\\ffmpeg.exe"                
        #voice_channel.play(discord.FFmpegPCMAudio(executable="caminho", source=filename))
        
        voice_channel.play(discord.FFmpegPCMAudio(filename, **ffmpeg_options))

    except Exception as err:
        print(err)
        return

@bot.command(name='pause', help='Pausa a música atual')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        embed = mensagem("","","","Pausando a música.")
        await ctx.send(embed=embed)
        await voice_client.pause()
    else:
        embed = mensagem("","","","O bot não está tocando no momento.")
        await ctx.send(embed=embed)
    
@bot.command(name='resume', help='Continua com a música')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client:
        if voice_client.is_paused():
            embed = mensagem("","","","Continuando com a música.")
            await ctx.send(embed=embed)
            voice_client.resume()
        else:
            embed = mensagem("","","","O bot não tem nada para tocar.")
            await ctx.send(embed=embed)
    else:
        embed = mensagem("","","","O bot não está no canal de voz.")
        await ctx.send(embed=embed)


@bot.command(name='stop', help='Para a música')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        embed = mensagem("","","","Parando a música.")
        await ctx.send(embed=embed)
        await voice_client.stop()
    else:
        embed = mensagem("","","","O bot não está tocando no momento.")
        await ctx.send(embed=embed)

@bot.command(name='cavalo', help='CAVALO')
async def cavalo(ctx):
    try :
        await join(ctx)

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            embed = mensagem("","","","Parando a música.")
            await ctx.send(embed=embed)
            voice_client.stop()

        url = 'https://www.youtube.com/watch?v=1xzGPPxKgJM'
        server = ctx.message.guild
        voice_channel = server.voice_client

        filename = await YTDLSource.from_url(url, loop=bot.loop)
        voice_channel.play(discord.FFmpegPCMAudio(filename, **ffmpeg_options))

        embed = mensagem("","","",'**CAVALO**')

        await ctx.send(embed=embed)
    except Exception as err:
        print(err)
        return

@bot.command(name='rapaiz', help='RAPAAAAAIZZZZZZ')
async def cavalo(ctx):
    try :
        await join(ctx)
        
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            embed = discord.Embed()
            embed.color = 2123412
            embed.description = "Parando a música."
            await ctx.send(embed=embed)
            voice_client.stop()

        url = 'https://www.youtube.com/watch?v=HXYNW0ft5o4'
        server = ctx.message.guild
        voice_channel = server.voice_client

        filename = await YTDLSource.from_url(url, loop=bot.loop)            
        voice_channel.play(discord.FFmpegPCMAudio(filename, **ffmpeg_options))

        embed = mensagem("","","",'**RAPAAAAAIZZZZZZ**')

        await ctx.send(embed=embed)
    except Exception as err:
        print(err)
        return

@bot.command(name='apresentar', help='Apresenta dados sobre o servidor')
async def apresentar(ctx):
        msgs = ['O bot está on!', 'O Pai tá on!', 'Alguém me chamou?!', 'Opa eae!']
        gifs = ['hunters', 'dancing_dante','all_good_bb','ghostface1']

        file1 = discord.File('./gifs/'+str(random.choice(gifs)+'.gif'), filename='image.gif')
        file2 = discord.File('./icon.png', filename='icon.png')

        title = 'Informações do server:'
        url1='attachment://icon.png'
        url2='attachment://image.gif'
        description = "\n\n*"+str(random.choice(msgs))+"*\n\n"

        embed = mensagem(title,url1,url2,description)

        embed.add_field(name="Criador(a): ", value=str(ctx.guild.owner), inline=False)
        embed.add_field(name="Servidor: ", value=str(ctx.guild.name), inline=False)
        embed.add_field(name="Quantia de membros: ", value=str(ctx.guild.member_count), inline=False)
        
        await ctx.send(files=[file1,file2], embed=embed)

@bot.command(name='help', help='Esta função exibe os comandos do bot')
async def help(ctx):
    try:
        
        description ="/help - Esta função exibe os comandos do bot\n"
        description+="/join - Chama o bot para o chat de voz\n"
        description+="/play <url> - Toca a musica especificada pela url em seguida\n"
        description+="/leave - Abandona o chat de voz\n"
        description+="/pause - Pausa a música atual\n"
        description+="/resume - Continua com a música\n"
        description+="/stop - Para a música\n"
        description+="/apresentar - Apresenta dados sobre o servidor\n"
        
        file1 = discord.File('./icon.png', filename='icon.png')
        
        title = 'Lista de Comandos:'
        url = 'attachment://icon.png'
        
        embed = mensagem(title,url,"",description)
        embed.add_field(name='Em desenvolvimento:', value='/surv_build - Apresenta uma build de DBD para o survivor\n', inline=False)
        

        await ctx.send(files=[file1], embed=embed)
    except Exception as err:
        print(err)
        return

def mensagem(title,url1,url2,description):
    embed = discord.Embed()
    embed.color = 2123412
    embed.title = title
    embed.set_thumbnail(url=url1)
    embed.set_image(url=url2)
    embed.description = description
    return embed

if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)

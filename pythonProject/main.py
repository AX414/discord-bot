import discord
import os
import asyncio
import ffmpeg
import random
import json
from deep_translator import GoogleTranslator
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
        self.thumbnail = data.get('thumbnail')
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
        imagem = str(data['thumbnail'])
        #ainda dá para adicionar mais coisas

        embed = mensagem("","",imagem,"**Título:  **"+titulo_video)
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
    if voice_client:
        if voice_client.is_connected():
            embed = mensagem("","","","Desconectando do canal de voz.")
            await ctx.send(embed=embed)
            await voice_client.disconnect()
        else:
            embed = mensagem("","","","O bot não está conectado à um canal de voz.")
            await ctx.send(embed=embed)
    else:
        embed = mensagem("","","","O bot não está no canal de voz.")
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
    if voice_client:
        if voice_client.is_playing():
            embed = mensagem("","","","Pausando a música.")
            await ctx.send(embed=embed)
            await voice_client.pause()
        else:
            embed = mensagem("","","","O bot não está tocando no momento.")
            await ctx.send(embed=embed)
    else:
        embed = mensagem("","","","O bot não está no canal de voz.")
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
    if voice_client:
        if voice_client.is_playing():
            embed = mensagem("","","","Parando a música.")
            await ctx.send(embed=embed)
            await voice_client.stop()
        else:
            embed = mensagem("","","","O bot não está tocando no momento.")
            await ctx.send(embed=embed)
    else:
        embed = mensagem("","","","O bot não está no canal de voz.")
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

        filename = await YTDLSource.from_url(url, loop=bot.loop, ctx=ctx)
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

        filename = await YTDLSource.from_url(url, loop=bot.loop, ctx=ctx)            
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

        file1 = discord.File('./images/gifs/'+str(random.choice(gifs)+'.gif'), filename='image.gif')
        file2 = discord.File('./images/survivor.png', filename='survivor.png')

        title = 'Informações do server:'
        url1='attachment://survivor.png'
        url2='attachment://image.gif'

        description = "\n\n*"+str(random.choice(msgs))+"*\n\n"

        embed = mensagem(title,url1,url2,description)

        embed.add_field(name="Criador(a): ", value=str(ctx.guild.owner), inline=False)
        embed.add_field(name="Servidor: ", value=str(ctx.guild.name), inline=False)
        embed.add_field(name="Quantia de membros: ", value=str(ctx.guild.member_count), inline=False)
        
        await ctx.send(files=[file1,file2], embed=embed)

@bot.command(name='info', help='Apresenta uma build de DBD para o killer')
async def info(ctx,arg):
    await info(ctx,arg)

@bot.command(name='surv_build', help='Apresenta uma build de DBD para o survivor')
async def surv_build(ctx):
    await randomizar(ctx,"Survivor","survivor")

@bot.command(name='killer_build', help='Apresenta uma build de DBD para o killer')
async def surv_build(ctx):
    await randomizar(ctx,"Killer","killer")

@bot.command(name='all_survs', help='Apresenta todos os sobreviventes')
async def all_killers(ctx):
    await apresentarTodos(ctx,"survivor")

@bot.command(name='all_killers', help='Apresenta todos os killers')
async def all_killers(ctx):
    await apresentarTodos(ctx,"killer")

@bot.command(name='help', help='Esta função exibe os comandos do bot')
async def help(ctx):
    try:
        
        description ='/help - Esta função exibe os comandos do bot\n'
        description+='/join - Chama o bot para o chat de voz\n'
        description+='/play <url> ou "pesquisa" - Toca a musica especificada pela url em seguida\n'
        description+='/leave - Abandona o chat de voz\n'
        description+='/pause - Pausa a música atual\n'
        description+='/resume - Continua com a música\n'
        description+='/stop - Para a música\n'
        description+='/apresentar - Apresenta dados sobre o servidor\n\n\n**Funções do DBD:**\n'
        description+='/info "Nome correto do personagem" - Apresenta informações do personagem especificado\n'
        description+='/surv_build - Apresenta uma build de DBD para o sobrevivente\n'
        description+='/killer_build - Apresenta uma build de DBD para o killer\n'
        description+='/all_survs - Apresenta todos os sobreviventes\n'
        description+='/all_killers - Apresenta todos os killers\n'
        
        file1 = discord.File('./images/survivor.png', filename='survivor.png')
        
        title = 'Lista de Comandos:'
        url = 'attachment://survivor.png'
        
        embed = mensagem(title,url,"",description)

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

async def info(ctx,arg):
    arquivo1= open('./jsons/characters2.json', "r")
    characters = json.loads(arquivo1.read())

    try:
        achou = False
        for value in characters.values():
            if value['name'] == str(arg):
                achou = True
                
                bio = '{}'.format(value['bio'])

                bio_traduzida = GoogleTranslator(source='auto', target='pt').translate(bio)

                embed = mensagem("Informações de {}:".format(value['name']),"","","")

                url = value['image']
                if url.startswith('h'):
                    embed.set_image(url=value['image'])

                embed.add_field(name="Bio:", value="{}".format(bio_traduzida), inline = False)
                await ctx.send(embed = embed)
                return
            else:
                achou = False
    except Exception:
        embed = mensagem("","","","Infelizmente o discord não permite mensagens muito grandes.")
        return
    
    if achou is False:
        embed = mensagem("","","","Não encontrei dados sobre esse personagem.")
        await ctx.send(embed = embed)

async def randomizar(ctx,role,arg):
    arquivo1= open('./jsons/characters2.json', "r")
    characters = json.loads(arquivo1.read())

    arquivo2 = open('./jsons/perks.json', "r")
    perks = json.loads(arquivo2.read())

    lista = []
    url = ''
    for value in characters.values():
        if value['role'] == str(arg):
            lista.append(value)
            if value['role'] == 'killer':
                file = discord.File('./images/killer.png', filename='icon.png')
            elif value['role'] == 'survivor':
                file = discord.File('./images/survivor.png', filename='icon.png')
                
    url = 'attachment://icon.png'

    i = 0
    personagem = str(random.choice(lista)['name'])
    habilidades = []

    for value in perks.values():
        if value['role'] == str(arg):
            habilidades.append(value)

    perk1 = random.choice(habilidades)
    habilidades.remove(perk1)
    perk2 = random.choice(habilidades)
    habilidades.remove(perk2)
    perk3 = random.choice(habilidades)
    habilidades.remove(perk3) 
    perk4 = random.choice(habilidades)
    habilidades.remove(perk4)

    d1 = GoogleTranslator(source='auto', target='pt').translate(perk1['name'])
    d2 = GoogleTranslator(source='auto', target='pt').translate(perk2['name'])
    d3 = GoogleTranslator(source='auto', target='pt').translate(perk3['name'])
    d4 = GoogleTranslator(source='auto', target='pt').translate(perk4['name'])
    
    embed = mensagem("Build do {}:".format(role),"","","Personagem: {}".format(personagem))
    embed.set_thumbnail(url=url)

    embed.add_field(name="\n{}".format(perk1['name']), value="Tradução: "+d1, inline = False)
    embed.add_field(name="\n{}".format(perk2['name']), value="Tradução: "+d2, inline = False)
    embed.add_field(name="\n{}".format(perk3['name']), value="Tradução: "+d3, inline = False)
    embed.add_field(name="\n{}".format(perk4['name']), value="Tradução: "+d4, inline = False)

    await ctx.send(files=[file], embed = embed)

async def apresentarTodos(ctx, role):
    arquivo1= open('./jsons/characters2.json', "r")
    characters = json.loads(arquivo1.read())

    var = ""
    for value in characters.values():
        if value['role'] == str(role):
            var += value['name']+"\n"

    embed = mensagem("Apresentando todos os {}:".format(role),"","","{}".format(var))
    await ctx.send(embed = embed)

if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)

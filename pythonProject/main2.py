import discord
import os
import asyncio
import random
import json
from deep_translator import GoogleTranslator
import requests
import yt_dlp as youtube_dl
from dotenv import load_dotenv
from discord.ext import commands
from fuzzywuzzy import process, fuzz  # Add this line
from io import BytesIO
from PIL import Image

load_dotenv()

DISCORD_TOKEN = os.getenv('MORI')

print(DISCORD_TOKEN)

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='/', intents=intents)

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

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.7):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.duration_string = data.get('duration_string')
        self.original_url = data.get('original_url')
        self.channel = data.get('channel')

    @classmethod
    async def from_query(cls, query, ctx):
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
        if 'entries' in data:
            data = data['entries'][0]

        titulo_video = str(data['title'])
        imagem = str(data['thumbnail'])
        duracao = str(data['duration_string'])
        url = str(data['original_url'])
        canal = str(data['channel'])

        embed = mensagem("", "", imagem, f"**Título: **{titulo_video}\n**Canal: ** {canal}\n**Duração: **{duracao}")
        embed.set_footer(text=f"URL: {url}")

        await ctx.send(embed=embed)

        return data['url']

# Remove o comando de ajuda padrão, decidi criar o meu próprio
bot.remove_command('help')

@bot.event
async def on_ready():
    print("Bot pronto.")

@bot.command(name='join', help='Chama o bot para o chat de voz')
async def join(ctx):
    if not ctx.author.voice:
        embed = mensagem("", "", "", "{} não está conectado à um canal de voz".format(ctx.author.name))
        await ctx.send(embed=embed)
        return
    else:
        voice_client = ctx.guild.voice_client
        if not voice_client:
            embed = mensagem("", "", "", "Conectando ao canal de voz.")
            await ctx.send(embed=embed)
            
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            embed = mensagem("", "", "", "O bot já está conectado ao canal de voz.")
            await ctx.send(embed=embed)

@bot.command(name='leave', help='Para expulsar o bot')
async def leave(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client:
        if voice_client.is_connected():
            embed = mensagem("", "", "", "Desconectando do canal de voz.")
            await ctx.send(embed=embed)
            await voice_client.disconnect()
        else:
            embed = mensagem("", "", "", "O bot não está conectado à um canal de voz.")
            await ctx.send(embed=embed)
    else:
        embed = mensagem("", "", "", "O bot não está no canal de voz.")
        await ctx.send(embed=embed)

@bot.command(name='play', help='Toca a música especificada pela url ou pesquisa')
async def play(ctx, *, query):
    try:
        await join(ctx)

        voice_client = ctx.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()

        url = await YTDLSource.from_query(query, ctx)
        
        voice_client.play(discord.FFmpegPCMAudio(executable="C:\\ffmpeg\\bin\\ffmpeg.exe", source=url))

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

@bot.command(name='apresentar', help='Apresenta dados sobre o servidor')
async def apresentar(ctx):
    msgs = [
        'Você entregou a alma pro diabo assim que vacilou comigo.\n(Caleb Quinn)',
        'Temos que trabalhar como um time. Eu preciso que vocês sobrevivam para que eu possa sobreviver!\n(Dwight Fairfield)',
        'Conhecimento básico de botânica poderia salvar sua vida um dia.\n(Claudette Morel)',
        'Prestar atenção é o que me manteve vivo ao longo dos anos. Isso e minha boa aparência, é claro.\n(Ace Visconti)'
    ]
    
    gifs_folder = './images/gifs/'
    gifs = [f for f in os.listdir(gifs_folder) if f.endswith('.gif')]

    chosen_gif = random.choice(gifs)
    file1 = discord.File(os.path.join(gifs_folder, chosen_gif), filename='image.gif')
    file2 = discord.File('./images/survivor.png', filename='survivor.png')

    title = 'Informações do server:'
    url1 = 'attachment://survivor.png'
    url2 = 'attachment://image.gif'

    description = "\n\n*" + random.choice(msgs) + "*\n\n"

    embed = mensagem(title, url1, url2, description)

    embed.add_field(name="Criador(a): ", value=str(ctx.guild.owner), inline=False)
    embed.add_field(name="Servidor: ", value=str(ctx.guild.name), inline=False)
    embed.add_field(name="Quantia de membros: ", value=str(ctx.guild.member_count), inline=False)

    await ctx.send(files=[file1, file2], embed=embed)

@bot.command(name='info', help='Apresenta uma build de DBD para o killer')
async def info(ctx, *, arg):
    await info(ctx,arg)

@bot.command(name='sb', help='Apresenta uma build de DBD para o survivor')
async def surv_build(ctx):
    await randomizar(ctx,"Survivor","survivor")

@bot.command(name='kb', help='Apresenta uma build de DBD para o killer')
async def killer_build(ctx):
    await randomizar(ctx,"Killer","killer")

@bot.command(name='alls', help='Apresenta todos os sobreviventes')
async def all_killers(ctx):
    await apresentarTodos(ctx,"survivor")

@bot.command(name='allk', help='Apresenta todos os killers')
async def all_killers(ctx):
    await apresentarTodos(ctx,"killer")

@bot.command(name='help', help='Esta função exibe os comandos do bot')
async def help(ctx):
    try:
        
        description ='/help - Esta função exibe os comandos do bot\n'
        description+='/join - Chama o bot para o chat de voz\n'
        description+='/play <url> ou *nome* - Toca a musica especificada pela url em seguida\n'
        description+='/leave - Abandona o chat de voz\n'
        description+='/pause - Pausa a música atual\n'
        description+='/resume - Continua com a música\n'
        description+='/stop - Para a música\n'
        description+='/apresentar - Apresenta dados sobre o servidor\n\n\n**Funções do DBD:**\n'
        description+='/info *nome do personagem* - Apresenta informações do personagem especificado\n'
        description+='/sb - Apresenta uma build de DBD para o sobrevivente\n'
        description+='/kb - Apresenta uma build de DBD para o killer\n'
        description+='/alls - Apresenta todos os sobreviventes\n'
        description+='/allk - Apresenta todos os killers\n'
        
        file1 = discord.File('./images/survivor.png', filename='survivor.png')
        
        title = 'Lista de Comandos:'
        url = 'attachment://survivor.png'
        
        embed = mensagem(title,url,"",description)

        await ctx.send(files=[file1], embed=embed)
    except Exception as err:
        print(err)
        return

def mensagem(title,url1,url2,description):

    #default = 0
    #teal = 0x1abc9c
    #dark_teal = 0x11806a
    #green = 0x2ecc71
    #dark_green = 0x1f8b4c
    #blue = 0x3498db
    #dark_blue = 0x206694
    #purple = 0x9b59b6
    #dark_purple = 0x71368a
    magenta = 0xe91e63
    #dark_magenta = 0xad1457
    #gold = 0xf1c40f
    #dark_gold = 0xc27c0e
    #orange = 0xe67e22
    #dark_orange = 0xa84300
    #red = 0xe74c3c
    #dark_red = 0x992d22
    #lighter_grey = 0x95a5a6
    #dark_grey = 0x607d8b
    #light_grey = 0x979c9f
    #darker_grey = 0x546e7a
    #blurple = 0x7289da
    #greyple = 0x99aab5

    embed = discord.Embed()
    embed.color = magenta
    embed.title = title
    embed.set_thumbnail(url=url1)
    embed.set_image(url=url2)
    embed.description = description
    return embed

async def info(ctx, arg):
    arquivo1 = open('./jsons/characters2.json', encoding="utf8")
    characters = json.loads(arquivo1.read())

    try:
        achou = False
        found_character = None
        max_score = 0

        for value in characters.values():
            score = process.extractOne(arg, [value['name']], scorer=fuzz.ratio)[1]

            if score >= 80:  # Ajuste o limite de pontuação conforme necessário
                achou = True
                found_character = value
                break
            elif score > max_score:
                max_score = score
                found_character = value

        if achou and found_character is not None:
            bio = '{}'.format(found_character['bio'])
            bio_traduzida = GoogleTranslator(source='auto', target='pt').translate(bio)

            # Verifica o tamanho do conteúdo do embed
            embed_content = f"Informações de {found_character['name']}:\n\nBio: {bio_traduzida}"
            if len(embed_content) > 2000:  # Limite do Discord para embeds
                await ctx.send(f"As informações sobre {found_character['name']} são muito extensas para serem exibidas aqui.")
            else:
                embed = mensagem(f"Informações de {found_character['name']}:", "", "", "{bio_traduzida}")
                url = found_character['image']
                if url.startswith('h'):
                    embed.set_image(url=found_character['image'])
                await ctx.send(embed=embed)
        else:
            embed = mensagem("", "", "", f"Não encontrei dados sobre '{arg}'.")
            await ctx.send(embed=embed)

    except Exception as e:
        print(e)
        embed = mensagem("", "", "", "Ocorreu um erro ao processar a solicitação.")
        await ctx.send(embed=embed)
        


async def randomizar(ctx, role, arg):
    progress_message = await ctx.send("Iniciando geração da build... 0%")

    def update_progress(step, total_steps):
        progress = int((step / total_steps) * 100)
        return f"Geração da build... {progress}%"

    total_steps = 10
    current_step = 0

    def update_progress_message():
        nonlocal current_step
        current_step += 1
        progress = update_progress(current_step, total_steps)
        return progress

    # Atualizando progresso
    await progress_message.edit(content=update_progress_message())

    arquivo1 = open('./jsons/characters2.json', encoding="utf8")
    characters = json.loads(arquivo1.read())

    arquivo2 = open('./jsons/perks2.json', encoding="utf8")
    perks = json.loads(arquivo2.read())

    lista = []
    for value in characters.values():
        if value['role'] == str(arg):
            lista.append(value)
            if value['role'] == 'killer':
                file = discord.File('./images/killer.png', filename='icon.png')
            elif value['role'] == 'survivor':
                file = discord.File('./images/survivor.png', filename='icon.png')

    url_thumb = 'attachment://icon.png'

    # Atualizando progresso
    await progress_message.edit(content=update_progress_message())

    random.seed(random.randint(0, 100000))
    personagem = random.choice(lista)
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

    # Atualizando progresso
    await progress_message.edit(content=update_progress_message())

    # Baixa as imagens das perks 
    perk_images = []
    for perk in [perk1, perk2, perk3, perk4]:
        response = requests.get(perk['image'])
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
        perk_images.append(img)

    # Atualizando progresso
    await progress_message.edit(content=update_progress_message())

    # Baixa a imagem do personagem 
    response = requests.get(personagem['image'])
    character_image = Image.open(BytesIO(response.content)).convert("RGBA")
    character_image = character_image.resize((character_image.width * 6, character_image.height * 6), Image.LANCZOS)

    # Atualizando progresso
    await progress_message.edit(content=update_progress_message())

    # Abre a imagem de fundo e redimensiona para preencher 100% da largura e altura da nova imagem
    background = Image.open('./images/banner.png')
    bg_width, bg_height = background.size
    new_height = max(bg_height, character_image.height) + 300  # Ajusta a altura da nova imagem
    new_width = int(bg_width * (new_height / bg_height))
    background = background.resize((new_width, new_height), Image.LANCZOS)

    # Atualizando progresso
    await progress_message.edit(content=update_progress_message())

    new_width = bg_width + character_image.width + 288  # Ajusta a largura da nova imagem
    new_height = max(bg_height, character_image.height) + 300  # Ajusta a altura da nova imagem
    combined_image = Image.new('RGBA', (new_width, new_height))

    # Cola a imagem de fundo na nova imagem
    combined_image.paste(background, (0, 0))

    # Atualizando progresso
    await progress_message.edit(content=update_progress_message())

    # Cola a imagem do personagem na nova imagem
    combined_image.paste(character_image, (1000, (new_height - character_image.height) // 4), character_image)

    # Atualizando progresso
    await progress_message.edit(content=update_progress_message())

    # Define posições para colar as perks na imagem de fundo em formato de cruz, no lado direito
    center_x = new_width - 2480
    center_y = new_height // 4

    positions = [
        (center_x, center_y - 432),  # Perk 1 (cima)
        (center_x - 432, center_y),  # Perk 2 (esquerda)
        (center_x + 432, center_y),  # Perk 3 (direita)
        (center_x, center_y + 432)   # Perk 4 (baixo)
    ]

    # Cola as imagens das perks na imagem de fundo
    for img, pos in zip(perk_images, positions):
        combined_image.paste(img, pos, img)

    # Atualizando progresso
    await progress_message.edit(content=update_progress_message())

    # Salva a imagem combinada em um buffer de bytes
    buffer = BytesIO()
    combined_image.save(buffer, format="PNG")
    buffer.seek(0)

    # Atualizando progresso
    await progress_message.edit(content=update_progress_message())

    embed = mensagem("Build do {}:".format(role),"","","Personagem: {}".format(personagem['name']))
    embed.set_thumbnail(url=url_thumb)
    embed.set_image(url=f"attachment://combined_perks.png")

    embed.add_field(name="\n{}".format(perk1['name']), value="Tradução: " + d1, inline=False)
    embed.add_field(name="\n{}".format(perk2['name']), value="Tradução: " + d2, inline=False)
    embed.add_field(name="\n{}".format(perk3['name']), value="Tradução: " + d3, inline=False)
    embed.add_field(name="\n{}".format(perk4['name']), value="Tradução: " + d4, inline=False)

    combined_file = discord.File(fp=buffer, filename='combined_perks.png')
    await ctx.send(files=[file, combined_file], embed=embed)

    # Finaliza progresso
    await progress_message.edit(content="Build gerada com sucesso! 100%")

async def apresentarTodos(ctx, role):
    arquivo1= open('./jsons/characters2.json', encoding="utf8")
    characters = json.loads(arquivo1.read())

    var = ""
    for value in characters.values():
        if value['role'] == str(role):
            var += value['name']+"\n"

    embed = mensagem("Apresentando todos os {}:".format(role),"","","{}".format(var))
    await ctx.send(embed = embed)

if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)

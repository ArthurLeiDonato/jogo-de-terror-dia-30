import pygame
import sys
import os
import random

# ==========================================
# 1. INICIALIZAÇÃO
# ==========================================
pygame.init()
pygame.mixer.init()

LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Escape Room - Edição Sombria (Estilo Rusty Lake)")

# Paleta de Cores
COR_BG_EXTERNO = (15, 15, 18)
COR_CONTORNO = (30, 30, 35)
DOURADO = (212, 175, 55)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO_SANGUE = (139, 0, 0)

fonte = pygame.font.SysFont("arial", 16)
fonte_negrito = pygame.font.SysFont("arial", 16, bold=True)
fonte_grande = pygame.font.SysFont("arial", 26, bold=True)
fonte_enorme = pygame.font.SysFont("arial", 42, bold=True)


# ==========================================
# 2. CLASSE PARA OBJETOS E BOTÕES
# ==========================================
class ObjetoGrafico:
    def __init__(self, x, y, largura, altura, cor_base, texto="", cor_texto=BRANCO, tipo="retangulo"):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor_base = cor_base
        self.texto = texto
        self.cor_texto = cor_texto
        self.tipo = tipo
        self.visivel = True

    def desenhar(self, surface):
        if not self.visivel:
            return
        
        if self.tipo == "porta":
            pygame.draw.rect(surface, (40, 30, 25), self.rect, border_radius=4)
            porta_interna = self.rect.inflate(-8, -8)
            pygame.draw.rect(surface, self.cor_base, porta_interna, border_radius=4)
            pygame.draw.rect(surface, COR_CONTORNO, self.rect, 3, border_radius=4)
            pygame.draw.circle(surface, DOURADO, (self.rect.x + 15, self.rect.centery), 5)
            pygame.draw.circle(surface, COR_CONTORNO, (self.rect.x + 15, self.rect.centery), 5, 1)

            if self.texto:
                txt_surf = fonte_negrito.render(self.texto, True, COR_CONTORNO)
                txt_rect = txt_surf.get_rect(center=(self.rect.centerx, self.rect.y - 15))
                surface.blit(txt_surf, txt_rect)
        else:
            sombra_rect = self.rect.copy()
            sombra_rect.y += 4
            pygame.draw.rect(surface, (120, 115, 105), sombra_rect, border_radius=6)
            pygame.draw.rect(surface, self.cor_base, self.rect, border_radius=6)
            pygame.draw.rect(surface, COR_CONTORNO, self.rect, 3, border_radius=6)

            if self.texto:
                txt_surf = fonte_negrito.render(self.texto, True, self.cor_texto)
                txt_rect = txt_surf.get_rect(center=self.rect.center)
                surface.blit(txt_surf, txt_rect)

    def foi_clicado(self, pos_mouse):
        return self.visivel and self.rect.collidepoint(pos_mouse)


# ==========================================
# 3. ESTADOS, IMAGENS E SONS
# ==========================================
sala_atual = "sala_principal"

inventario = []
mensagem_status = "Você está no Hall Principal. Escolha uma porta para entrar."

# Estados de Progresso dos Puzzles
cofre_aberto = False

susto_ativo = False
tempo_susto = 0
duracao_susto_ms = 1000

# --- CARREGAR MÚSICA DE FUNDO COM CAMINHO SEGURO ---
try:
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_musica = os.path.join(diretorio_atual, "1-01. Eisoptrophobia_2.mp3")
    
    if os.path.exists(caminho_musica):
        pygame.mixer.music.load(caminho_musica)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
        print("Sucesso: A música de fundo começou a tocar!")
    else:
        print(f"Aviso: O ficheiro de áudio não foi encontrado no caminho: {caminho_musica}")
except Exception as e:
    print(f"Erro crítico ao carregar a música: {e}")

# --- CARREGAR IMAGENS DE FUNDO E REAIS ---
def carregar_imagem(caminho, largura, altura):
    if os.path.exists(caminho):
        try:
            img = pygame.image.load(caminho).convert()
            return pygame.transform.scale(img, (largura, altura))
        except pygame.error:
            return None
    return None

# Fundos das Salas
img_bg_principal = carregar_imagem("WhatsApp Image 2026-10-29 at 18.40.32.jpeg", 720, 440)
img_bg_relogio = carregar_imagem("WhatsApp Image 2026-10-29 at 12.11.51 (2).jpeg", 720, 440)
img_bg_mesa = carregar_imagem("WhatsApp Image 2026-10-29 at 12.11.51 (1).jpeg", 720, 440)
img_bg_fuga = carregar_imagem("WhatsApp Image 2026-10-29 at 18.38.56.jpeg", 720, 440)

# Cofre (Fechado e Aberto)
img_bg_cofre_fechado = carregar_imagem("WhatsApp Image 2026-10-29 at 12.11.51.jpeg", 720, 440)
img_bg_cofre_aberto = carregar_imagem("cofre_aberto.jpeg", 720, 440)

# Sala Escura / Iluminada (Porta da Lâmpada)
img_bg_escura = carregar_imagem("WhatsApp Image 2026-10-29 at 18.38.55.jpeg", 720, 440)
img_bg_iluminada = carregar_imagem("WhatsApp Image 2026-10-29 at 18.38.54.jpeg", 720, 440)

# --- CARREGAR FRAMES DA ANIMAÇÃO DO SUSTO ---
frames_susto = []
arquivos_susto = [
    "WhatsApp Image 2026-10-30 at 13.35.22.jpeg",
    "WhatsApp Image 2026-10-29 at 22.04.08.jpeg"
]

for nome_arq in arquivos_susto:
    if os.path.exists(nome_arq):
        try:
            img_f = pygame.image.load(nome_arq).convert_alpha()
            frames_susto.append(pygame.transform.scale(img_f, (450, 450)))
        except pygame.error:
            pass

if not frames_susto and os.path.exists("flavio.png"):
    try:
        img_unico = pygame.image.load("flavio.png").convert_alpha()
        frames_susto.append(pygame.transform.scale(img_unico, (450, 450)))
    except pygame.error:
        pass

# Som do Susto
som_susto = None
if os.path.exists("susto.mp3"):
    try:
        som_susto = pygame.mixer.Sound("susto.mp3")
        duracao_susto_ms = int(som_susto.get_length() * 1000)
    except pygame.error:
        pass

# --- DICIONÁRIO DE MAPEAMENTO EXATO: HORÁRIO -> IMAGEM DO RELÓGIO ---
imagens_relogio_por_horario = {
    (1, 40): carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.19 (2).jpeg", 350, 350),
    (2, 0):  carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.19 (3).jpeg", 350, 350),
    (2, 20): carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.18 (1).jpeg", 350, 350),
    (3, 45): carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.18.jpeg", 350, 350),
    (5, 50): carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.18 (2).jpeg", 350, 350),
    (6, 0):  carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.19 (1).jpeg", 350, 350),
    (12, 0): carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.19.jpeg", 350, 350),
    (7, 15): carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.20 (1).jpeg", 350, 350),
    (8, 30): carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.20 (2).jpeg", 350, 350),
    (9, 0):  carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.20 (3).jpeg", 350, 350),
    (10, 10): carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.20.jpeg", 350, 350),
    (11, 20): carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.21 (1).jpeg", 350, 350),
    (4, 15): carregar_imagem("WhatsApp Image 2026-10-29 at 15.10.21 (2).jpeg", 350, 350),
}

horarios_validos = list(imagens_relogio_por_horario.keys())
indice_horario_atual = 0

# --- BOTÕES DE INTERFACE ---
btn_voltar_hub = ObjetoGrafico(55, 415, 140, 35, (180, 90, 90), "<- Voltar ao Hall")
btn_botao_saida = ObjetoGrafico(350, 230, 90, 35, VERMELHO_SANGUE, "saida")

# Botões de Zoom do Relógio
btn_voltar_zoom = ObjetoGrafico(50, 420, 100, 35, (180, 90, 90), "<- Voltar")
btn_horario_ant = ObjetoGrafico(520, 180, 155, 45, (70, 70, 80), "< Horário")
btn_horario_prox = ObjetoGrafico(520, 235, 155, 45, (70, 70, 80), "Horário >")
btn_confirmar_relogio = ObjetoGrafico(520, 310, 155, 45, (50, 140, 70), "Confirmar Hora")

relogio = pygame.time.Clock()


# ==========================================
# 4. LOOP PRINCIPAL DO JOGO
# ==========================================
while True:
    tempo_atual = pygame.time.get_ticks()

    if susto_ativo and (tempo_atual - tempo_susto > duracao_susto_ms):
        susto_ativo = False

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                pos = evento.pos

                def disparar_susto():
                    global susto_ativo, tempo_susto
                    susto_ativo = True
                    tempo_susto = pygame.time.get_ticks()
                    if som_susto:
                        som_susto.play()

                # --- CLIQUE NA BARRA DE INVENTÁRIO (INSPEÇÃO DE ITENS) ---
                if sala_atual in ["sala_principal", "sala_relogio", "sala_mesa", "sala_cofre", "sala_fuga", "sala_escura"] and pos[1] >= 525:
                    for i, item in enumerate(inventario):
                        x_slot = 120 + (i * 115)
                        rect_slot = pygame.Rect(x_slot, 538, 105, 50)
                        if rect_slot.collidepoint(pos):
                            if item == "Vela":
                                mensagem_status = "Descrição: Uma vela de cera amarelada. Ilumina ambientes escuros."
                            elif item == "Pista do Relógio":
                                mensagem_status = "Descrição: O quadro mostra um relógio com os ponteiros às 03:45."
                            elif item == "Óleo de Graxa":
                                mensagem_status = "Descrição: Um frasco de óleo lubrificante para abrir mecanismos emperrados."
                            elif item == "Código do Cofre":
                                mensagem_status = "Descrição: O código secreto obtido no cofre."
                            elif item == "Chave da Saída":
                                mensagem_status = "Descrição: A chave pesada encontrada no cofre para abrir a saída."

                # --- SALA PRINCIPAL (HALL COM AS 5 PORTAS) ---
                elif sala_atual == "sala_principal":
                    if pos[0] >= 75 and pos[0] <= 175 and pos[1] >= 130 and pos[1] <= 390:
                        sala_atual = "sala_escura"
                        if "Vela" in inventario:
                            if "Óleo de Graxa" not in inventario:
                                inventario.append("Óleo de Graxa")
                                mensagem_status = "Você entrou na sala com a vela, iluminou o ambiente e encontrou o Óleo de Graxa!"
                            else:
                                mensagem_status = "Você entrou na sala iluminada."
                        else:
                            mensagem_status = "Você entrou na sala escura. Está tudo muito escuro!"

                    elif pos[0] >= 205 and pos[0] <= 305 and pos[1] >= 130 and pos[1] <= 390:
                        sala_atual = "sala_mesa"
                        mensagem_status = "Você entrou na Sala da Mesa."

                    elif pos[0] >= 335 and pos[0] <= 435 and pos[1] >= 130 and pos[1] <= 390:
                        sala_atual = "sala_fuga"
                        mensagem_status = "Você chegou à Porta de Fuga."

                    elif pos[0] >= 465 and pos[0] <= 565 and pos[1] >= 130 and pos[1] <= 390:
                        sala_atual = "sala_cofre"
                        mensagem_status = "Você entrou na Sala do Cofre."

                    elif pos[0] >= 595 and pos[0] <= 695 and pos[1] >= 130 and pos[1] <= 390:
                        sala_atual = "sala_relogio"
                        mensagem_status = "Você entrou na Sala do Relógio."

                # --- SALA ESCURA ---
                elif sala_atual == "sala_escura":
                    if btn_voltar_hub.foi_clicado(pos):
                        sala_atual = "sala_principal"
                        mensagem_status = "Você voltou ao Hall Principal."

                # --- SALA DA PORTA DE FUGA (BOTÃO "saida") ---
                elif sala_atual == "sala_fuga":
                    if btn_voltar_hub.foi_clicado(pos):
                        sala_atual = "sala_principal"
                        mensagem_status = "Você voltou ao Hall Principal."
                    
                    elif btn_botao_saida.foi_clicado(pos):
                        if "Código do Cofre" in inventario and "Chave da Saída" in inventario:
                            sala_atual = "vitoria"
                            mensagem_status = "Você usou os itens corretos e escapou!"
                        else:
                            disparar_susto()
                            sala_atual = "sala_principal"
                            inventario.clear() 
                            cofre_aberto = False
                            mensagem_status = "Você tentou sair, tomou um susto e voltou ao início!"

                # --- SALA DO RELÓGIO ---
                elif sala_atual == "sala_relogio":
                    if btn_voltar_hub.foi_clicado(pos):
                        sala_atual = "sala_principal"
                        mensagem_status = "Você voltou ao Hall Principal."
                    elif pos[0] >= 120 and pos[0] <= 240 and pos[1] >= 100 and pos[1] <= 260:
                        if "Pista do Relógio" not in inventario:
                            inventario.append("Pista do Relógio")
                            mensagem_status = "Você examinou o quadro: marca 03:45!"
                        else:
                            mensagem_status = "O quadro mostra um relógio pintado às 03:45."
                    elif pos[0] >= 340 and pos[0] <= 460 and pos[1] >= 150 and pos[1] <= 390:
                        sala_atual = "zoom_relogio"
                        mensagem_status = "Ajuste os ponteiros do relógio antigo."

                # --- SALA DA MESA ---
                elif sala_atual == "sala_mesa":
                    if btn_voltar_hub.foi_clicado(pos):
                        sala_atual = "sala_principal"
                        mensagem_status = "Você voltou ao Hall Principal."
                    elif pos[0] >= 150 and pos[0] <= 570 and pos[1] >= 180 and pos[1] <= 400:
                        if "Vela" not in inventario:
                            inventario.append("Vela")
                            mensagem_status = "Você pegou a Vela da mesa!"
                        else:
                            mensagem_status = "A mesa já está limpa."

                # --- SALA DO COFRE ---
                elif sala_atual == "sala_cofre":
                    if btn_voltar_hub.foi_clicado(pos):
                        sala_atual = "sala_principal"
                        mensagem_status = "Você voltou ao Hall Principal."
                    elif not cofre_aberto:
                        if pos[0] >= 200 and pos[0] <= 600 and pos[1] >= 100 and pos[1] <= 420:
                            if "Óleo de Graxa" in inventario:
                                cofre_aberto = True
                                mensagem_status = "Você aplicou o Óleo de Graxa e abriu o cofre pesado!"
                            else:
                                mensagem_status = "O cofre está emperrado e enferrujado. Precisa de Óleo de Graxa!"
                    else:
                        if pos[0] >= 250 and pos[0] <= 550 and pos[1] >= 150 and pos[1] <= 380:
                            if "Código do Cofre" not in inventario or "Chave da Saída" not in inventario:
                                if "Código do Cofre" not in inventario:
                                    inventario.append("Código do Cofre")
                                if "Chave da Saída" not in inventario:
                                    inventario.append("Chave da Saída")
                                mensagem_status = "Você recolheu o Código do Cofre e a Chave da Saída de dentro do cofre!"
                            else:
                                mensagem_status = "O cofre já está vazio."

                # --- ZOOM DO RELÓGIO ---
                elif sala_atual == "zoom_relogio":
                    if btn_voltar_zoom.foi_clicado(pos):
                        sala_atual = "sala_relogio"
                        mensagem_status = "Você se afastou do relógio."
                    elif btn_horario_ant.foi_clicado(pos):
                        indice_horario_atual = (indice_horario_atual - 1) % len(horarios_validos)
                    elif btn_horario_prox.foi_clicado(pos):
                        indice_horario_atual = (indice_horario_atual + 1) % len(horarios_validos)
                    elif btn_confirmar_relogio.foi_clicado(pos):
                        hora_atual, min_atual = horarios_validos[indice_horario_atual]
                        if hora_atual == 3 and min_atual == 45:
                            mensagem_status = "O mecanismo do relógio está estável. (A chave principal está agora no cofre!)"
                        else:
                            mensagem_status = "Nada aconteceu. Horário incorreto."
                            if random.random() < 0.4:
                                disparar_susto()


    # ==========================================
    # 5. RENDERIZAÇÃO E DESIGN VISUAL
    # ==========================================
    tela.fill(COR_BG_EXTERNO)
    viewport_rect = pygame.Rect(40, 20, 720, 440)

    if sala_atual == "sala_principal":
        if img_bg_principal:
            tela.blit(img_bg_principal, (40, 20))
        else:
            pygame.draw.rect(tela, (25, 22, 28), viewport_rect)
        pygame.draw.rect(tela, COR_CONTORNO, viewport_rect, 4)

    elif sala_atual == "sala_escura":
        if "Vela" in inventario:
            if img_bg_iluminada:
                tela.blit(img_bg_iluminada, (40, 20))
            else:
                pygame.draw.rect(tela, (100, 90, 80), viewport_rect)
            titulo = fonte_grande.render("Sala Iluminada pela Vela", True, BRANCO)
        else:
            if img_bg_escura:
                tela.blit(img_bg_escura, (40, 20))
            else:
                pygame.draw.rect(tela, (10, 10, 10), viewport_rect)
            titulo = fonte_grande.render("Sala Escura", True, BRANCO)

        pygame.draw.rect(tela, COR_CONTORNO, viewport_rect, 4)
        tela.blit(titulo, (65, 30))
        btn_voltar_hub.desenhar(tela)

    elif sala_atual == "sala_fuga":
        if img_bg_fuga:
            tela.blit(img_bg_fuga, (40, 20))
        else:
            pygame.draw.rect(tela, (30, 30, 30), viewport_rect)
        pygame.draw.rect(tela, COR_CONTORNO, viewport_rect, 4)
        titulo = fonte_grande.render("Sala de Fuga", True, BRANCO)
        tela.blit(titulo, (65, 30))
        btn_voltar_hub.desenhar(tela)
        btn_botao_saida.desenhar(tela)

    elif sala_atual in ["sala_relogio", "sala_mesa", "sala_cofre"]:
        if sala_atual == "sala_relogio":
            if img_bg_relogio:
                tela.blit(img_bg_relogio, (40, 20))
            else:
                pygame.draw.rect(tela, (200, 200, 190), viewport_rect)
            titulo = fonte_grande.render("Sala do Relógio", True, BRANCO)

        elif sala_atual == "sala_mesa":
            if img_bg_mesa:
                tela.blit(img_bg_mesa, (40, 20))
            else:
                pygame.draw.rect(tela, (150, 140, 130), viewport_rect)
            titulo = fonte_grande.render("Sala da Mesa e Velas", True, BRANCO)

        elif sala_atual == "sala_cofre":
            if cofre_aberto:
                if img_bg_cofre_aberto:
                    tela.blit(img_bg_cofre_aberto, (40, 20))
                else:
                    pygame.draw.rect(tela, (80, 70, 60), viewport_rect)
            else:
                if img_bg_cofre_fechado:
                    tela.blit(img_bg_cofre_fechado, (40, 20))
                else:
                    pygame.draw.rect(tela, (50, 50, 50), viewport_rect)
            titulo = fonte_grande.render("Sala do Cofre", True, BRANCO)

        pygame.draw.rect(tela, COR_CONTORNO, viewport_rect, 4)
        tela.blit(titulo, (65, 30))
        btn_voltar_hub.desenhar(tela)

    elif sala_atual == "zoom_relogio":
        pygame.draw.rect(tela, (30, 24, 18), viewport_rect)
        pygame.draw.rect(tela, COR_CONTORNO, viewport_rect, 4)

        titulo = fonte_grande.render("MECANISMO DO RELÓGIO", True, DOURADO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 35))

        h_atual, m_atual = horarios_validos[indice_horario_atual]
        img_atual_rel = imagens_relogio_por_horario.get((h_atual, m_atual), None)

        if img_atual_rel:
            tela.blit(img_atual_rel, (120, 80))

        str_horario = f"{h_atual:02d}:{m_atual:02d}"
        txt_horario = fonte_negrito.render(f"Horário: {str_horario}", True, DOURADO)
        tela.blit(txt_horario, (530, 130))

        btn_voltar_zoom.desenhar(tela)
        btn_horario_ant.desenhar(tela)
        btn_horario_prox.desenhar(tela)
        btn_confirmar_relogio.desenhar(tela)

        lbl_navegacao = fonte.render("SELECIONAR HORÁRIO", True, BRANCO)
        tela.blit(lbl_navegacao, (525, 155))

    elif sala_atual == "vitoria":
        tela.fill((10, 20, 15))
        txt_vitoria = fonte_enorme.render("PARABÉNS!", True, DOURADO)
        txt_sub = fonte_grande.render("Você escapou do casarão sombrio com vida!", True, BRANCO)
        tela.blit(txt_vitoria, (LARGURA // 2 - txt_vitoria.get_width() // 2, 200))
        tela.blit(txt_sub, (LARGURA // 2 - txt_sub.get_width() // 2, 270))

    # --- EFEITO DE SUSTO COM ANIMAÇÃO DINÂMICA ---
    if susto_ativo:
        tela.fill((40, 0, 0))
        if frames_susto:
            indice_frame = (tempo_atual // 150) % len(frames_susto)
            img_atual = frames_susto[indice_frame]
            pos_x = (LARGURA - img_atual.get_width()) // 2
            pos_y = (ALTURA - img_atual.get_height()) // 2
            tela.blit(img_atual, (pos_x, pos_y))
        else:
            txt_susto = fonte_enorme.render("BOO!", True, BRANCO)
            tela.blit(txt_susto, (LARGURA // 2 - txt_susto.get_width() // 2, ALTURA // 2 - 25))

    # --- HUD INFERIOR (STATUS E INVENTÁRIO) ---
    if not susto_ativo and sala_atual != "vitoria":
        pygame.draw.rect(tela, (230, 225, 210), (40, 475, 720, 40), border_radius=4)
        pygame.draw.rect(tela, COR_CONTORNO, (40, 475, 720, 40), 2, border_radius=4)
        txt_msg = fonte_negrito.render(mensagem_status, True, COR_CONTORNO)
        tela.blit(txt_msg, (55, 486))

        pygame.draw.rect(tela, (25, 25, 30), (0, 525, LARGURA, 75))
        pygame.draw.line(tela, (70, 70, 80), (0, 525), (LARGURA, 525), 3)
        txt_inv = fonte.render("INVENTÁRIO:", True, BRANCO)
        tela.blit(txt_inv, (15, 552))

        for i, item in enumerate(inventario):
            x_slot = 120 + (i * 115)
            pygame.draw.rect(tela, (45, 45, 55), (x_slot, 538, 105, 50), border_radius=4)
            pygame.draw.rect(tela, DOURADO, (x_slot, 538, 105, 50), 2, border_radius=4)
            txt_item = fonte.render(item, True, DOURADO)
            tela.blit(txt_item, (x_slot + 6, 555))

    pygame.display.flip()
    relogio.tick(60)
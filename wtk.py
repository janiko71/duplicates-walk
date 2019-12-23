# https://pythonprogramming.net/community/698/Sqlite3%20and%20Tkinter%20How%20to%20perform%20select%20statment%20so%20that%20result%20display%20on%20GUI%20/

import io, os, sys

# GUI/Interface graphique

from tkinter.filedialog import *
from tkinter import *
import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.font as tkFont
from tkinter import ttk

win32 = (sys.platform == 'win32')

# ==================================================================================
#
#  Classe pour l'Application graphique (de type Tkinter)
#
# ==================================================================================

class App(tk.Frame):

    #
    # Constructeur
    #

    # ------------------------------
    def __init__(self, master=None):
    # ------------------------------

        super().__init__(master)
        self.pack()
        self.create_layout()
    
    #
    # Fonction coeur de l'IHM : creéation des objets graphiques
    #

    # ------------------------------
    def create_layout(self):
    # ------------------------------


        #
        #  Définition de l'écran d'IHM
        #
        """
            Fontes de caractères
        """

        if win32:

            font_mono = tkFont.Font(family='consolas', size=8)
            font_mono_it = tkFont.Font(family='consolas', size=8, slant='italic')
            font_calib = tkFont.Font(family='Calibri', size=9)
            font_calib_bold = tkFont.Font(family='Calibri', size=11, weight='bold')

        else:

            font_mono = tkFont.Font(family='monospace', size=8)
            font_mono_it = tkFont.Font(family='monospace', size=8, slant='italic')
            font_calib = tkFont.Font(family='Calibri', size=8)
            font_calib_bold = tkFont.Font(family='Calibri', size=10, weight='bold')


        """
            Cadre principal
        """

        self.main_frame = Frame(self, relief='solid')
        self.main_frame.pack()


        """
        #
        # On aura besoin de quelques fonctions pour accéder aux éléments de l'IHM
        #

        # Fonctions utilisées pour la gestion de l'IHM
        # -----

        # ------------------------------
        def get_position():
        # ------------------------------

            # Retourne la position de la sélection actuelle
            
            global myapp

            return myapp.f_qrcodes.curselection()[0] 


        # ------------------------------
        def action_affiche_qr_code():
        # ------------------------------

            # Fonction permettant de savoir si on a déjà lu un fichier de QR Codes ou pas

            if fichier_deja_ouvert():  

                pos = get_position()
                affiche_qr_code(qrcodes[pos])


        # ------------------------------
        def ouvrir_fichier():
        # ------------------------------

            # Ouverture et lecture du fichier de QR Codes (si un fichier est sélectionné). Il doit être sur un lecteur amovible ('/media')
            # Le fichier à lire doit être la version chiffrée (cryptée ;) dont le suffixe est .qraws

            global myapp, qrcodes, file_path

            file_path = tk.filedialog.askopenfilename(defaultextension='.qraws', initialdir='/media')

            if not(mode_test):

                # On n'est pas en mode test, donc le fichier doit être sur un média amovible
                if file_path[0:6] != "/media":
                    msgbox.showerror("Erreur fichier","Attention : il est INTERDIT d'écrire le fichier ailleurs que sur un support amovible !")
                    file_path = ""

            # On vérifie l'extension du fichier
            file_ext = os.path.splitext(file_path)[1]
            if (file_ext != ".qraws"):
                msgbox.showerror("Erreur fichier","Attention : Le fichier en entrée doit être chiffré et finir par l\'extension .qraws !")
                file_path = ""

            if (file_path != ""):
                qrcodes = lecture_QR(file_path)
                remplissage_QR()
                myapp.focus_set()

            return file_path


        # ------------------------------
        def remplissage_QR():
        # ------------------------------

            # Remplissage de la liste des QR Codes

            global qrcodes

            liste_qr = []
            for i in range(0, len(qrcodes)):
                liste_qr.append(str(qrcodes[i]))
            myapp.liste_qr.set(liste_qr)


        # ------------------------------
        # Fonctions de gestion des touches pour le widget 'liste des qrcodes'
        # ------------------------------

        # ------------------------------
        def event_affiche_qr_code(event):
        # ------------------------------

            action_affiche_qr_code()
        

        # ------------------------------
        def next_item(event):
        # ------------------------------

            pos = get_position()
            if (pos < self.f_qrcodes.size() - 1):
                self.f_qrcodes.selection_clear(pos)
                self.f_qrcodes.selection_set(pos + 1)


        # ------------------------------
        def prev_item(event):
        # ------------------------------

            pos = get_position()
            if (pos > 0):
                self.f_qrcodes.selection_clear(pos)
                self.f_qrcodes.selection_set(pos - 1)



        """
        #    Panel à gauche (info, aide, boutons d'action)
        """

        self.left_frame = Frame(self.main_frame, padx=20, pady=10, relief='solid',)
        self.left_frame.grid(column=0, row=0)
        
        # Titre de l'application
        # ...

        self.label_title = Label(self.left_frame, text=init_text_title, font="Courier 11", fg="green", justify=LEFT)
        self.label_title.grid(column=0, row=0)

        # Boutons d'action (fenetre f_ctrl)
        # ...

        # ---------------------------------------- titre cadre
        self.f_ctrl = LabelFrame(self.left_frame, text="  Commandes  ", bd=1, relief='solid', labelanchor=N, padx=20, pady=20, width=70)

        # ---------------------------------------- btn ouvrir fichier
        self.b_ouvrir = tk.Button(self.f_ctrl, command=ouvrir_fichier, text="Ouvrir un fichier", width=30, pady=1, font=font_calib, fg="black", bg="#ddd")
        self.b_ouvrir.grid(row=0)

        # ---------------------------------------- espace
        Label(self.f_ctrl, width=50).grid(row=1)

        # ---------------------------------------- btn ajout QR code root
        self.b_add_root = tk.Button(self.f_ctrl, command=partial(ajout_qr_code, is_root=True), text="Ajouter QR root", width=30, pady=1, font=font_calib, fg="black", bg="#ddd")
        self.b_add_root.grid(row=2)

        # ---------------------------------------- btn ajout QR code utilisateur IAM
        self.b_add_user = tk.Button(self.f_ctrl, command=partial(ajout_qr_code, is_root=False), text="Ajouter QR user", width=30, pady=1, font=font_calib, fg="black", bg="#ddd")
        self.b_add_user.grid(row=3)

        # ---------------------------------------- btn afficher QR code
        self.b_print_qr = tk.Button(self.f_ctrl, text="Afficher QR", command=action_affiche_qr_code, width=30, pady=1, font=font_calib, fg="black", bg="#ddd")
        self.b_print_qr.grid(row=4)

        # ---------------------------------------- espace
        Label(self.f_ctrl, width=50).grid(row=5)

        # ---------------------------------------- btn export clé AES vers KeySecure
        self.b_print_qr = tk.Button(self.f_ctrl, text="Export clé AES", command=export_cle_aes, width=30, pady=1, font=font_calib, fg="black", bg="#ddd")
        self.b_print_qr.grid(row=6)

        # ---------------------------------------- espace
        Label(self.f_ctrl, width=50).grid(row=7)

        # ---------------------------------------- btn quitter
        self.quit = tk.Button(self.f_ctrl, text="Quitter", padx=16, pady=1, font=font_calib, fg="black", bg="#ddd",  command=self.master.destroy)
        self.quit.grid(row=8)

        # Affichage de la fenêtre f_ctrl
        # ...

        self.f_ctrl.grid(column=0, row=1)

        # Fenêtre d'aide (f_help)
        # ...

        self.f_help = LabelFrame(self.left_frame, text="  Aide  ", bd=1, relief='solid', labelanchor=N, padx=20, pady=10)
        f_txt = Text(self.f_help, bg=self.cget("background"), font=font_calib, relief='flat', wrap='word', width=70, height=14)
        f_txt.tag_config('titre', font=font_calib_bold)
        f_txt.insert('end', "Programme de gestion des QR Codes pour AWS", 'titre')
        f_txt.insert('end', help_txt_1)
        f_txt.insert('end', help_txt_2)
        f_txt.insert('end', help_txt_3)
        f_txt.pack()

        # Affichage de la fenêtre f_help
        # ...        

        self.f_help.grid(column=0, row=3)


        """
        #    Panel à droite : liste des QR Codes déjà connus
        """

        self.right_frame = Frame(self.main_frame, padx=20, pady=10)
        self.right_frame.grid(column=1, row=0, rowspan=3)

        # Liste des QR Codes
        # ...

        # Widget d'affichage des QR codes
        # ...

        # On ne peut sélectionner qu'une ligne à la fois (selectmode='single')

        legende_txt = " {}   {:<20}   {:<16}   {:<30}    {:<20}   {:<12}         ".format("type","identifiant","user","alias/num_ordre", "issuer", "account")
        legende = Label(self.right_frame, text=legende_txt, font=font_mono_it, fg='gray', justify=LEFT, width=126)
        legende.pack()

        self.liste_qr = Variable(self.right_frame, ())
        scrollbar = tk.Scrollbar(self.right_frame, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)

        self.f_qrcodes = Listbox(self.right_frame, listvariable=self.liste_qr, selectmode="single", bg='WhiteSmoke',
                            font=font_mono, width=126, height=45, 
                            selectbackground="seagreen", highlightcolor="black", activestyle='none', 
                            yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.f_qrcodes.yview)

        self.f_qrcodes.pack(side=TOP, expand=True)

        # Gestion des touches et de la souris pour la liste des QR codes

        self.f_qrcodes.bind("<Key-Return>", event_affiche_qr_code)
        self.f_qrcodes.bind("<Key-Down>", next_item)
        self.f_qrcodes.bind("<Key-Up>", prev_item)

    """

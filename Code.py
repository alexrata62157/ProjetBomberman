#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import os
import sys
import glob
from time import *
from random import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from Animation import *

class ImageTuto(QLabel):     # Permet d'implémenter des images dans la fenêtre tuto
    def __init__(self,w,h,imgName):
        super().__init__()
        image = QPixmap(imgName)
        image = image.scaled(w,h,Qt.KeepAspectRatio)
        self.setPixmap(image)

class TextImg(QLabel):       # Fait apparaitre des chaînes de caractères dans la fenêtre tuto
    def __init__(self,txt):
        super().__init__()
        self.setText(txt)

class Window(QMainWindow):   # Permet de faire apparaître notre la tuto
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Tutoriel')
        self.tuto()

    def paintEvent(self, e):
        painter=QPainter(self)
        for b in self.blocks:
            painter.drawPixmap(QRect(b.y,b.x,100,100),b.image)

    def tuto(self):
        fen = QDialog(self)
        layout= QGridLayout()
        w =50
        h =50
        imgA = ImageTuto(w,h,"TUto/A.png")
        imgQ = ImageTuto(w,h,"TUto/Q.png")
        imgD = ImageTuto(w,h,"TUto/D.png")
        imgS = ImageTuto(w,h,"TUto/S.png")
        imgZ = ImageTuto(w,h,"TUto/Z.png")
        imgHaut = ImageTuto(w,h,"TUto/Haut.png")
        imgBas = ImageTuto(w,h,"TUto/Bas.png")
        imgDroite = ImageTuto(w,h,"TUto/Droite.png")
        imgGauche = ImageTuto(w,h,"TUto/Gauche.png")
        imgSpace = ImageTuto(w,h,"TUto/Espace.png")
        imgJ1 = ImageTuto(w,h,"Image/Perso/bas/1.png")
        imgJ2 = ImageTuto(w,h,"Image/Perso2/bas/1.png")
        layout.addWidget(imgJ1,0,1)
        layout.addWidget(imgJ2,0,2)
        layout.addWidget(TextImg("Joueur 1"),1,1)
        layout.addWidget(TextImg("Joueur 2"),1,2)
        layout.addWidget(TextImg("Haut"),2,0)
        layout.addWidget(TextImg("Bas"),3,0)
        layout.addWidget(TextImg("Gauche"),4,0)
        layout.addWidget(TextImg("Droite"),5,0)
        layout.addWidget(TextImg("Bombe"),6,0)
        layout.addWidget(imgHaut,2,1)
        layout.addWidget(imgBas,3,1)
        layout.addWidget(imgGauche,4,1)
        layout.addWidget(imgDroite,5,1)
        layout.addWidget(imgSpace,6,1)
        layout.addWidget(imgZ,2,2)
        layout.addWidget(imgS,3,2)
        layout.addWidget(imgQ,4,2)
        layout.addWidget(imgD,5,2)
        layout.addWidget(imgA,6,2)

        fen.setLayout(layout)
        fen.setWindowTitle('Tutoriel')
        fen.show()

    def quit(self):
        dialog = QMessageBox();
        dialog.setText("Voulez-vous vraiment quitter?")
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        dialog.setDefaultButton(QMessageBox.Ok)
        if dialog.exec_() == QMessageBox.Ok:
             QCoreApplication.instance().quit()

class Joueur1(Objet):        # Création du premier personnage

    def __init__(self, scene,x=0,y=0):
        super().__init__(scene, x,y)
        self.animations.add("down", glob.glob(r"Image/Perso/bas/*.png"),interval = 50)       # Création des sprites pour les déplacements (suite d'images)
        self.animations.add("up", glob.glob(r"Image/Perso/haut/*.png"),interval = 50)
        self.animations.add("right", glob.glob(r"Image/Perso/droite/*.png"),interval = 50)
        self.animations.add("left", glob.glob(r"Image/Perso/droite/*.png"), interval=50, horizontal_flip=True)
        self.imageDefaut("down")
        # Rectangle de collision autour du personnage (égal à la taille d'une case)
        self.collision_rect = QRect(0, 0, 80, 80)
        self.vitesse = 16
        self.puissance = 1    # Variable concernant la taille de l'explosion
        self.compteur = 1    # Variable concernant le nombre de bombes plaçables
        self.now = 0      # Variable concernant le nombre de bombes actuellement plaçées

    def deplacerBas(self):  # Gestion des déplacements
        self.setY(self.y() + self.vitesse)

    def deplacerHaut(self):
        self.setY(self.y() - self.vitesse)

    def deplacerGauche(self):
        self.setX(self.x() - self.vitesse)

    def deplacerDroite(self):
        self.setX(self.x() + self.vitesse)

    # Gestion des commandes de déplacement + utilisation des sprites
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Down:
            if (self.y()+80 < self.scene.height()):
                self.animations.play("down", self.deplacerBas)
        if key == Qt.Key_Up:
            if (self.y()-80 >= 0):
                self.animations.play("up", self.deplacerHaut)
        if key == Qt.Key_Left:
            if (self.x() > 0):
                self.animations.play("left", self.deplacerGauche)
        if key == Qt.Key_Right:
            if (self.x()+80 < self.scene.width()):
                self.animations.play("right", self.deplacerDroite)
        if key == 32:
            if(self.now < self.compteur):
                xc = (self.x()+40)//80*80
                yc = (self.y()+40)//80*80
                self.now = self.now+1
                bombe = Bombe(self.scene, puissance=self.puissance, x=xc, y=yc)

    def collision(self, other):
        # Collision avec l'IA, les flammes de l'IA ou les flammes du joueur 2
        if(type(other) == Flamme or type(other) == Flamme1 or type(other) == IA1 or type(other) == IA2 or type(other) == IA3):
            QSound.play("./sons/mort.wav")
            m = Message(self.scene)
            m.add("Player 1 lose")
            self.detruire()
            re=Rejouer(scene,180,100)
            re.show()
        if(type(other) == Block):
            self.setX((self.x()+40)//80*80)
            self.setY((self.y()+40)//80*80)
        if(type(other) == Booster):   # Collision avec un booster
            if(other.uptype == "BombPower"):
                self.compteur = self.compteur+1
                other.detruire()
            if(other.uptype == "FlamePower"):
                self.puissance = self.puissance+1
                other.detruire()
        if(self.x() == 1200 and self.y() == 640):
            m = Message(self.scene)
            m.add("Mission complete!")
            self.detruire()
            re=Rejouer(scene,180,100)
            re.show()

class Joueur2(Objet):        # Créer un personnage identique au premier, mis à part dans les raccourcis claviers et l'aspect physique
    def __init__(self, scene, x=0, y=0):
        super().__init__(scene, x, y)
        self.animations.add("down", glob.glob(r"Image/Perso2/bas/*.png"), interval=50)
        self.animations.add("up", glob.glob(r"Image/Perso2/haut/*.png"), interval=50)
        self.animations.add("right", glob.glob(r"Image/Perso2/droite/*.png"), interval=50)
        self.animations.add("left", glob.glob(r"Image/Perso2/droite/*.png"), interval=50, horizontal_flip=True)
        self.imageDefaut("down")
        self.collision_rect = QRect(0, 0, 80, 80)
        self.setZValue(0)
        self.puissance = 1
        self.vitesse = 16
        self.compteur = 1
        self.now = 0

    def deplacerBas(self):
        self.setY(self.y() + self.vitesse)

    def deplacerHaut(self):
        self.setY(self.y() - self.vitesse)

    def deplacerGauche(self):
        self.setX(self.x() - self.vitesse)

    def deplacerDroite(self):
        self.setX(self.x() + self.vitesse)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_S:
            if (self.y()+80 < self.scene.height()):
                self.animations.play("down", self.deplacerBas)
        if key == Qt.Key_Z:
            if (self.y()-80 >= 0):
                self.animations.play("up", self.deplacerHaut)
        if key == Qt.Key_Q:
            if (self.x() > 0):
                self.animations.play("left", self.deplacerGauche)
        if key == Qt.Key_D:
            if (self.x()+80 < self.scene.width()):
                self.animations.play("right", self.deplacerDroite)
        if key == Qt.Key_A:
            if(self.now < self.compteur):
                xc = (self.x()+40)//80*80
                yc = (self.y()+40)//80*80
                self.now = self.now+1
                bombe = Bombebis(self.scene, puissance=self.puissance, x=xc, y=yc)

    def collision(self, other):
        if(type(other) == Flamme ):
            QSound.play("./sons/mort.wav")
            m = Message(self.scene)
            m.add("Player 2 lose")
            self.detruire()
            re=Rejouer(scene,180,100)
            re.show()
        if(type(other) == Block):
            self.setX((self.x()+40)//80*80)
            self.setY((self.y()+40)//80*80)
        if(type(other) == Booster):
            if(other.uptype == "BombPower"):
                self.compteur = self.compteur+1
                other.detruire()
            if(other.uptype == "FlamePower"):
                self.puissance = self.puissance+1
                other.detruire()

class Image(QGraphicsItem):  # Classe qui permet d'implémenter un image
    def __init__(self, scene, x=0, y=0, path=None):
        super().__init__()
        self.scene = scene
        self.scene.addItem(self)
        self.image = QImage(path)
        self.width = self.image.width()
        self.height = self.image.height()
        self.setX(x)
        self.setY(y)

    def paint(self, painter, option, widget=None):
        if self.image:
            painter.drawImage(0, 0, self.image)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def detruire(self):
        if self in self.scene.items():
            self.scene.removeItem(self)

class Flamme(Objet):         # Classe de création des flammes après l'explosion de la bombe d'un joueur
    def __init__(self, scene, x=0, y=0, a=0):
        super().__init__(scene, x, y)
        self.animations.add("Flamme", glob.glob(                             # Gestions des sprites
            r"Image/Flamme/FlammeRouge/*.png"), interval=200)
        self.animations.add("Flamme1", glob.glob(
            r"Image/Flamme/FlammeBleu/*.png"), interval=200)
        self.animations.add("Flamme2", glob.glob(
            r"Image/Flamme/FlammeVerte/*.png"), interval=200)
        self.animations.add("Flamme3", glob.glob(
            r"Image/Flamme/FlammeViolette/*.png"), interval=200)

        # Choix des flammes ( 4 couleurs )
        if a == 0:
            self.animations.play("Flamme", on_transition=None, on_completion=self.detruire)
        if a == 1:
            self.animations.play("Flamme1", on_transition=None, on_completion=self.detruire)
        if a == 2:
            self.animations.play("Flamme2", on_transition=None,on_completion=self.detruire)
        if a == 3:
            self.animations.play("Flamme3", on_transition=None,on_completion=self.detruire)

    # Si les flammes touchent une autre bombe celle-ci explose et si elles touchent un booster celui-ci disparait
    def collision(self, other):
        if (type(other) == Booster):
            other.detruire()

class Flamme1(Objet):        # Classe de création des flammes après l'explosion de la bombe d'un joueur
    def __init__(self, scene, x=0, y=0, a=0):
        super().__init__(scene, x, y)
        self.animations.add("Flamme", glob.glob(                             # Gestions des sprites
            r"Image/Flamme/FlammeRouge/*.png"), interval=200)
        self.animations.add("Flamme1", glob.glob(
            r"Image/Flamme/FlammeBleu/*.png"), interval=200)
        self.animations.add("Flamme2", glob.glob(
            r"Image/Flamme/FlammeVerte/*.png"), interval=200)
        self.animations.add("Flamme3", glob.glob(
            r"Image/Flamme/FlammeViolette/*.png"), interval=200)

        # Choix des flammes ( 4 couleurs )
        if a == 0:
            self.animations.play("Flamme", on_transition=None, on_completion=self.detruire)
        if a == 1:
            self.animations.play("Flamme1", on_transition=None, on_completion=self.detruire)
        if a == 2:
            self.animations.play("Flamme2", on_transition=None,on_completion=self.detruire)
        if a == 3:
            self.animations.play("Flamme3", on_transition=None,on_completion=self.detruire)

    # Si les flammes touchent une autre bombe celle-ci explose et si elles touchent un booster celui-ci disparait
    def collision(self, other):
        if (type(other) == Booster):
            other.detruire()

class IA1(Objet):            # Création d'une IA
    def __init__(self, scene, x=0, y=0):
        super().__init__(scene, x, y)
        self.animations.add("down", glob.glob(r"Image/Creep/bas/*.png"), interval=50)                      # Sprites de déplacements de  l'IA
        self.animations.add("up", glob.glob(r"Image/Creep/haut/*.png"), interval=50)
        self.animations.add("right", glob.glob(r"Image/Creep/droite/*.png"), interval=50)
        self.animations.add("left", glob.glob(r"Image/Creep/droite/*.png"), interval=50, horizontal_flip=True)
        self.imageDefaut("down")
        self.vitesse = 10   # Vitesse de déplacement
        self.puissance = 1     # Taille des flammes
        self.compteur = 1    # Bombes posables
        self.now = 0       # Bombes actuellement posées
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        # Rectangle de collisions autour de l'IA
        self.collision_rect = QRect(0, 0, 80, 80)

    def start(self):
        self.timer.start(1000)

    def timeout(self):
        direction = randint(0, 3)  # Déplacements avec une direction aléatoire
        b = randint(0, 5)
        if(direction == 0) and (self.y()+80) < self.scene.height():
            self.animations.play("down", self.deplacerBas)
        if(direction == 1) and (self.y()-80) >= 0:
            self.animations.play("up", self.deplacerHaut)
        if(direction == 2) and (self.x() > 0):
            self.animations.play("left", self.deplacerGauche)
        if(direction == 3) and self.x()+80 < self.scene.width():
            self.animations.play("right", self.deplacerDroite)
        if b < 3:
            if(self.now < self.compteur):
                xc = (self.x()+40)//80*80
                yc = (self.y()+40)//80*80
                self.now = self.now+1
                bombe = Bombe1(self.scene, puissance=self.puissance, x=xc, y=yc)

    def deplacerBas(self):                            # Déplacements de l'IA
        self.setY(self.y() + self.vitesse)

    def deplacerHaut(self):
        self.setY(self.y() - self.vitesse)

    def deplacerGauche(self):
        self.setX(self.x() - self.vitesse)

    def deplacerDroite(self):
        self.setX(self.x() + self.vitesse)

    # Si l'IA est touché par la bombe d'un joueur, elle est détruite
    def collision(self, other):
        if(type(other) == Flamme):
            self.detruire()

        if(type(other) == Block):                   # Collision avec les murs
            self.setX((self.x()+40)//80*80)
            self.setY((self.y()+40)//80*80)

        if(type(other) == Booster):        # Collision avec un booster
            if(other.uptype == "FlamePower"):
                self.puissance = self.puissance+1
                other.detruire()

class IA2(Objet):
    def __init__(self, scene, x=0, y=0):
        super().__init__(scene, x, y)
        # Sprites de déplacements de  l'IA
        self.animations.add("down", glob.glob(r"Image/Creep/bas/*.png"), interval=50)                      # Sprites de déplacements de  l'IA
        self.animations.add("up", glob.glob(r"Image/Creep/haut/*.png"), interval=50)
        self.animations.add("right", glob.glob(r"Image/Creep/droite/*.png"), interval=50)
        self.animations.add("left", glob.glob(r"Image/Creep/droite/*.png"), interval=50, horizontal_flip=True)
        self.imageDefaut("down")
        self.vitesse = 10   # Vitesse de déplacement
        self.puissance = 1     # Taille des flammes
        self.compteur = 1    # Bombes posables
        self.now = 0       # Bombes actuellement posées
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        # Rectangle de collisions autour de l'IA
        self.collision_rect = QRect(0, 0, 80, 80)

    def start(self):
        self.timer.start(1000)

    def timeout(self):
        direction = randint(0, 3)  # Déplacements avec une direction aléatoire
        b = randint(0, 5)
        if(direction == 0) and (self.y()+80) < self.scene.height():
            self.animations.play("down", self.deplacerBas)
        if(direction == 1) and (self.y()-80) >= 0:
            self.animations.play("up", self.deplacerHaut)
        if(direction == 2) and (self.x() > 0):
            self.animations.play("left", self.deplacerGauche)
        if(direction == 3) and self.x()+80 < self.scene.width():
            self.animations.play("right", self.deplacerDroite)
        if b < 3:
            if(self.now < self.compteur):
                xc = (self.x()+40)//80*80
                yc = (self.y()+40)//80*80
                self.now = self.now+1
                bombe = Bombe2(self.scene, puissance=self.puissance, x=xc, y=yc)

    def deplacerBas(self):                            # Déplacements de l'IA
        self.setY(self.y() + self.vitesse)

    def deplacerHaut(self):
        self.setY(self.y() - self.vitesse)

    def deplacerGauche(self):
        self.setX(self.x() - self.vitesse)

    def deplacerDroite(self):
        self.setX(self.x() + self.vitesse)

    # Si l'IA est touché par la bombe d'un joueur, elle est détruite
    def collision(self, other):
        if(type(other) == Flamme):
            self.detruire()

        if(type(other) == Block):                   # Collision avec les murs
            self.setX((self.x()+40)//80*80)
            self.setY((self.y()+40)//80*80)

        if(type(other) == Booster):        # Collision avec un booster
            if(other.uptype == "FlamePower"):
                self.puissance = self.puissance+1
                other.detruire()

class IA3(Objet):
    def __init__(self, scene, x=0, y=0):
        super().__init__(scene, x, y)
        self.animations.add("down", glob.glob(r"Image/Creep/bas/*.png"), interval=50)                      # Sprites de déplacements de  l'IA
        self.animations.add("up", glob.glob(r"Image/Creep/haut/*.png"), interval=50)
        self.animations.add("right", glob.glob(r"Image/Creep/droite/*.png"), interval=50)
        self.animations.add("left", glob.glob(r"Image/Creep/droite/*.png"), interval=50, horizontal_flip=True)
        self.vitesse = 10   # Vitesse de déplacement
        self.puissance = 1     # Taille des flammes
        self.compteur = 1    # Bombes posables
        self.now = 0       # Bombes actuellement posées
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        # Rectangle de collisions autour de l'IA
        self.collision_rect = QRect(0, 0, 80, 80)

    def start(self):
        self.timer.start(1000)

    def timeout(self):
        direction = randint(0, 3)  # Déplacements avec une direction aléatoire
        b = randint(0, 5)
        if(direction == 0) and (self.y()+80) < self.scene.height():
            self.animations.play("down", self.deplacerBas)
        if(direction == 1) and (self.y()-80) >= 0:
            self.animations.play("up", self.deplacerHaut)
        if(direction == 2) and (self.x() > 0):
            self.animations.play("left", self.deplacerGauche)
        if(direction == 3) and self.x()+80 < self.scene.width():
            self.animations.play("right", self.deplacerDroite)
        if b < 3:
            if(self.now < self.compteur):
                xc = (self.x()+40)//80*80
                yc = (self.y()+40)//80*80
                self.now = self.now+1
                bombe = Bombe3(self.scene, puissance=self.puissance, x=xc, y=yc)

    def deplacerBas(self):                            # Déplacements de l'IA
        self.setY(self.y() + self.vitesse)

    def deplacerHaut(self):
        self.setY(self.y() - self.vitesse)

    def deplacerGauche(self):
        self.setX(self.x() - self.vitesse)

    def deplacerDroite(self):
        self.setX(self.x() + self.vitesse)

    # Si l'IA est touché par la bombe d'un joueur, elle est détruite
    def collision(self, other):
        if(type(other) == Flamme):
            self.detruire()

        if(type(other) == Block):                   # Collision avec les murs
            self.setX((self.x()+40)//80*80)
            self.setY((self.y()+40)//80*80)

        if(type(other) == Booster):        # Collision avec un booster
            if(other.uptype == "FlamePower"):
                self.puissance = self.puissance+1
                other.detruire()

class Sol(Objet):            # Création d'un sol
    def __init__(self,scene,x,y,blocktype = "sol"):
        super().__init__(scene,x,y)
        self.blocktype = blocktype
        self.animations.add("sol",['Image/sol.png'],non_stop=False)
        self.animations.add("fin",['Image/fin.png'],non_stop=False)
        self.imageDefaut(self.blocktype)

class unJoueur(Objet):       # Création d'un bouton pour lancer la partie (version bronze)
    def __init__(self,scene,x=0,y=0):
        super().__init__(scene,x,y)
        self.animations.add("normal",["Image/One_Player_Normal.png"],interval=1,non_stop = False)       # Gestions des images pour les boutons
        self.animations.add("hover",["Image/One_Player_Hover.png"],interval=1,non_stop = False)
        self.imageDefaut("normal")
        self.setAcceptHoverEvents(True)
        self.intro=QSound("./sons/Intro.wav")
        self.hover=QSound("./sons/hover.wav")
        self.start=QSound("./sons/start.wav")
        self.jeu=QSound("./sons/jeu.wav")
        self.jeu.setLoops(-1)
        self.intro.play()
        self.con=0

    def hoverEnterEvent(self, event):
        self.con=1
        self.animations.play("hover", None)
        self.hover.play()
                                                    # Images et sons en fonction de l'état du bouton
    def hoverLeaveEvent(self, event):
        self.con=0
        self.animations.play("normal", None)

    def mousePressEvent(self,event):            # Création de la partie (dans cet exemble ce sera le mode Solo vs IA (version bronze = sortir du labyrinthe, la sortie se trouvant dans le coin opposé au spawn Joueur)
        if self.con==1:
            self.start.play()
            self.jeu.play()

            for i,item in enumerate(self.scene.items()):
                if(item!=self):
                    item.detruire()
            pos=[[0,0],[80,0],[0,80],[0,640],[0,560],[80,640],[1200,0],[1120,0],[1200,80],[1200,640],[1120,640],[1200,560]]  # Positions des 4 Spawns (cases qui font angle)
            for i in range(0,16):
                Block(scene,i*80,-80,'solidblock')
                Block(scene,i*80,720,'solidblock')
                if i<9 :
                    Block(scene,-80,i*80,'solidblock')
                    Block(scene,1280,i*80,'solidblock')
                for j in range(0,9):
                    Sol(scene,i*80,j*80)                         # Remplir la matrice de l'image pour le sol
                    if (i*80==1200 and j*80 == 640):
                        Sol(scene,i*80,j*80, 'fin')
                    pos1=80*i
                    pos2=80*j
                    tmp=randint(0,3)
                    if i>0 and i<8and i%2!=0 and j>0 and j%2!=0 :
                        Block(scene,pos1,pos2,'solidblock')
                        pos.append([pos1,pos2])
                    if i>7 and i%2==0 and j>0 and j%2!=0 :
                        Block(scene,pos1,pos2,'solidblock')
                        pos.append([pos1,pos2])
                    if [pos1,pos2] not in pos and(tmp==1 or tmp==2 or tmp==3) :
                        Block(scene,80*i,80*j,'explodableblock')

            Ia2 = IA2(scene, 0, 640)
            Ia2.start()
            Ia1 = IA1(scene, 1200,0)
            Ia1.start()
            Ia3 = IA3(scene, 1200,640)
            Ia3.start()

            Joueur1(scene,0,0)              # Création du personnage
            self.detruire()

class deuxJoueurs(Objet):    # Identique à "unJoueur" sauf qu'au lieu de poser des IA on va poser un adversaire (version silver)
    def __init__(self,scene,x=0,y=0):
        super().__init__(scene,x,y)
        self.animations.add("normal",["Image/Two_Player_Normal.png"],interval=1,non_stop = False)
        self.animations.add("hover",["Image/Two_Player_Hover.png"],interval=1,non_stop = False)
        self.imageDefaut("normal")
        self.setAcceptHoverEvents(True)
        self.intro=QSound("./sons/Intro.wav")
        self.hover=QSound("./sons/hover.wav")
        self.start=QSound("./sons/start.wav")
        self.jeu=QSound("./sons/jeu.wav")
        self.jeu.setLoops(-1)
        self.intro.play()
        self.con=0

    def hoverEnterEvent(self, event):
        self.con=1
        self.animations.play("hover", None)
        self.hover.play()


    def hoverLeaveEvent(self,event):
        self.con=0
        self.animations.play("normal", None)

    def mousePressEvent(self,event):
        if self.con==1:
            self.start.play()
            self.jeu.play()
            for i,item in enumerate(self.scene.items()):
                if(item!=self):
                    item.detruire()

            pos=[[0,0],[80,0],[0,80],[0,640],[0,560],[80,640],[1200,0],[1120,0],[1200,80],[1200,640],[1120,640],[1200,560]]
            for i in range(0,16):
                Block(scene,i*80,-80,'solidblock')
                Block(scene,i*80,720,'solidblock')
                if i<9 :
                    Block(scene,-80,i*80,'solidblock')
                    Block(scene,1280,i*80,'solidblock')
                for j in range(0,9):
                    Sol(scene,i*80,j*80)                         # Remplir la matrice de l'image pour le sol
                    pos1=80*i
                    pos2=80*j
                    tmp=randint(0,3)
                    if i>0 and i<8and i%2!=0 and j>0 and j%2!=0 :
                        Block(scene,pos1,pos2,'solidblock')
                        pos.append([pos1,pos2])
                    if i>7 and i%2==0 and j>0 and j%2!=0 :
                        Block(scene,pos1,pos2,'solidblock')
                        pos.append([pos1,pos2])
                    if [pos1,pos2] not in pos and(tmp==1 or tmp==2 or tmp==3) :
                        Block(scene,80*i,80*j,'explodableblock')

            Joueur1(scene,0,0)
            Joueur2(scene, 1200, 640)
            self.detruire()

class Booster(Objet):        # Création des booster
    def __init__(self, scene, x=0, y=0, uptype="BombPower"):
        super().__init__(scene, x, y)
        self.animations.add(
            "BombPower", ['Image/Booster/BombPowerup.png'], non_stop=False)
        self.animations.add(
            "FlamePower", ['Image/Booster/FlamePowerup.png'], non_stop=False)
        self.uptype = uptype
        self.can_Destroy = True
        self.imageDefaut(self.uptype)

class Bombe(Objet):          # Création des bombes du/des joueur(s)
    def __init__(self, scene, puissance=1, x=0, y=0):
        super().__init__(scene, x, y)
        QSound.play("./sons/poserb.wav")
        self.animations.add("Bombe", glob.glob(r"Image/Bombe/*.png"), interval=200, repeat=6)
        self.imageDefaut("Bombe")
        self.puissance = puissance
        self.animations.play("Bombe", None, self.explosion)
        self.setZValue(0)

    def explosion(self):
        self.detruire()
        QSound.play("./sons/exploserb.wav")
        man = None
        for i, item in enumerate(self.scene.items()):
            if(type(item) == Joueur1 ):
                man = item
                man.now = man.now-1
        a = randint(0, 3)
        f = Flamme(self.scene, self.x(), self.y(), a)
        b1 = True
        b2 = True
        b3 = True
        b4 = True
        for i in range(1, self.puissance+1):
            if self.x()+80*i < self.scene.width() and b1 == True:
                if(self.checkBlock(self.x()+80*i, self.y()) == True):
                    f = Flamme(self.scene, self.x()+80*i, self.y(), a)
                else:
                    b1 = False
            if self.x()-80*i >= 0 and b2 == True:
                if(self.checkBlock(self.x()-80*i, self.y()) == True):
                    f = Flamme(self.scene, self.x()-80*i, self.y(), a)
                else:
                    b2 = False
            if self.y()-80*i >= 0 and b3 == True:
                if(self.checkBlock(self.x(), self.y()-80*i) == True):
                    f = Flamme(self.scene, self.x(), self.y()-80*i, a)
                else:
                    b3 = False
            if self.y()+80*i < self.scene.height() and b4 == True:
                if(self.checkBlock(self.x(), self.y()+80*i) == True):
                    f = Flamme(self.scene, self.x(), self.y()+80*i, a)
                else:
                    b4 = False

    def checkBlock(self, x, y):
        pt = True
        for i, item in enumerate(self.scene.items()):
            if(type(item) == Block):
                bx = item.x()
                by = item.y()
                if bx == x and by == y:
                    pt = False
                    if item.can_Destroy == True:
                        item.detruire()
                        z = randint(0, 100)
                        if(z <= 10):
                            up = Booster(self.scene, bx+8, by+8)
                        elif(z <= 20):
                            up = Booster(self.scene, bx+8, by+8, "FlamePower")
        return pt

class Bombebis(Objet):       # Création des bombes du/des joueur(s)
    def __init__(self, scene, puissance=1, x=0, y=0):
        super().__init__(scene, x, y)
        QSound.play("./sons/poserb.wav")
        self.animations.add("Bombe", glob.glob(r"Image/Bombe/*.png"), interval=200, repeat=6)
        self.imageDefaut("Bombe")
        self.puissance = puissance
        self.animations.play("Bombe", None, self.explosion)
        self.setZValue(0)

    def explosion(self):
        self.detruire()
        QSound.play("./sons/exploserb.wav")
        man = None
        for i, item in enumerate(self.scene.items()):
            if(type(item) == Joueur2 ):
                man = item
                man.now = man.now-1
        a = randint(0, 3)
        f = Flamme(self.scene, self.x(), self.y(), a)
        b1 = True
        b2 = True
        b3 = True
        b4 = True
        for i in range(1, self.puissance+1):
            if self.x()+80*i < self.scene.width() and b1 == True:
                if(self.checkBlock(self.x()+80*i, self.y()) == True):
                    f = Flamme(self.scene, self.x()+80*i, self.y(), a)
                else:
                    b1 = False
            if self.x()-80*i >= 0 and b2 == True:
                if(self.checkBlock(self.x()-80*i, self.y()) == True):
                    f = Flamme(self.scene, self.x()-80*i, self.y(), a)
                else:
                    b2 = False
            if self.y()-80*i >= 0 and b3 == True:
                if(self.checkBlock(self.x(), self.y()-80*i) == True):
                    f = Flamme(self.scene, self.x(), self.y()-80*i, a)
                else:
                    b3 = False
            if self.y()+80*i < self.scene.height() and b4 == True:
                if(self.checkBlock(self.x(), self.y()+80*i) == True):
                    f = Flamme(self.scene, self.x(), self.y()+80*i, a)
                else:
                    b4 = False

    def checkBlock(self, x, y):
        pt = True
        for i, item in enumerate(self.scene.items()):
            if(type(item) == Block):
                bx = item.x()
                by = item.y()
                if bx == x and by == y:
                    pt = False
                    if item.can_Destroy == True:
                        item.detruire()
                        z = randint(0, 100)
                        if(z <= 10):
                            up = Booster(self.scene, bx+8, by+8)
                        elif(z <= 20):
                            up = Booster(self.scene, bx+8, by+8, "FlamePower")
        return pt

class Bombe1(Objet):         # Création des bombes des IA
    def __init__(self, scene, puissance=1, x=0, y=0):
        super().__init__(scene, x, y)
        QSound.play("./sons/poserb.wav")
        self.animations.add("Bombe", glob.glob(r"Image/Bombe/*.png"), interval=200, repeat=6)
        self.imageDefaut("Bombe")
        self.puissance = puissance
        self.animations.play("Bombe", None, self.explosion)
        self.setZValue(0)

    def explosion(self):
        self.detruire()
        QSound.play("./sons/exploserb.wav")
        man = None
        for i, item in enumerate(self.scene.items()):
            if(type(item) == IA1):
                man = item
                man.now = man.now-1
        a = randint(0, 3)
        f = Flamme1(self.scene, self.x(), self.y(), a)
        b1 = True
        b2 = True
        b3 = True
        b4 = True
        for i in range(1, self.puissance+1):
            if self.x()+80*i < self.scene.width() and b1 == True:
                if(self.checkBlock(self.x()+80*i, self.y()) == True):
                    f = Flamme1(self.scene, self.x()+80*i, self.y(), a)
                else:
                    b1 = False
            if self.x()-80*i >= 0 and b2 == True:
                if(self.checkBlock(self.x()-80*i, self.y()) == True):
                    f = Flamme1(self.scene, self.x()-80*i, self.y(), a)
                else:
                    b2 = False
            if self.y()-80*i >= 0 and b3 == True:
                if(self.checkBlock(self.x(), self.y()-80*i) == True):
                    f = Flamme1(self.scene, self.x(), self.y()-80*i, a)
                else:
                    b3 = False
            if self.y()+80*i < self.scene.height() and b4 == True:
                if(self.checkBlock(self.x(), self.y()+80*i) == True):
                    f = Flamme1(self.scene, self.x(), self.y()+80*i, a)
                else:
                    b4 = False

    def checkBlock(self, x, y):
        pt = True
        for i, item in enumerate(self.scene.items()):
            if(type(item) == Block):
                bx = item.x()
                by = item.y()
                if bx == x and by == y:
                    pt = False
                    if item.can_Destroy == True:
                        item.detruire()
                        z = randint(0, 100)
                        if(z <= 10):
                            up = Booster(self.scene, bx+8, by+8)
                        elif(z <= 20):
                            up = Booster(self.scene, bx+8, by+8, "FlamePower")
        return pt

class Bombe2(Objet):         # Création des bombes des IA
    def __init__(self, scene, puissance=1, x=0, y=0):
        super().__init__(scene, x, y)
        QSound.play("./sons/poserb.wav")
        self.animations.add("Bombe", glob.glob(r"Image/Bombe/*.png"), interval=200, repeat=6)
        self.imageDefaut("Bombe")
        self.puissance = puissance
        self.animations.play("Bombe", None, self.explosion)
        self.setZValue(0)

    def explosion(self):
        self.detruire()
        QSound.play("./sons/exploserb.wav")
        man = None
        for i, item in enumerate(self.scene.items()):
            if(type(item) == IA2 ):
                man = item
                man.now = man.now-1
        a = randint(0, 3)
        f = Flamme1(self.scene, self.x(), self.y(), a)
        b1 = True
        b2 = True
        b3 = True
        b4 = True
        for i in range(1, self.puissance+1):
            if self.x()+80*i < self.scene.width() and b1 == True:
                if(self.checkBlock(self.x()+80*i, self.y()) == True):
                    f = Flamme1(self.scene, self.x()+80*i, self.y(), a)
                else:
                    b1 = False
            if self.x()-80*i >= 0 and b2 == True:
                if(self.checkBlock(self.x()-80*i, self.y()) == True):
                    f = Flamme1(self.scene, self.x()-80*i, self.y(), a)
                else:
                    b2 = False
            if self.y()-80*i >= 0 and b3 == True:
                if(self.checkBlock(self.x(), self.y()-80*i) == True):
                    f = Flamme1(self.scene, self.x(), self.y()-80*i, a)
                else:
                    b3 = False
            if self.y()+80*i < self.scene.height() and b4 == True:
                if(self.checkBlock(self.x(), self.y()+80*i) == True):
                    f = Flamme1(self.scene, self.x(), self.y()+80*i, a)
                else:
                    b4 = False

    def checkBlock(self, x, y):
        pt = True
        for i, item in enumerate(self.scene.items()):
            if(type(item) == Block):
                bx = item.x()
                by = item.y()
                if bx == x and by == y:
                    pt = False
                    if item.can_Destroy == True:
                        item.detruire()
                        z = randint(0, 100)
                        if(z <= 10):
                            up = Booster(self.scene, bx+8, by+8)
                        elif(z <= 20):
                            up = Booster(self.scene, bx+8, by+8, "FlamePower")
        return pt

class Bombe3(Objet):         # Création des bombes des IA
    def __init__(self, scene, puissance=1, x=0, y=0):
        super().__init__(scene, x, y)
        QSound.play("./sons/poserb.wav")
        self.animations.add("Bombe", glob.glob(r"Image/Bombe/*.png"), interval=200, repeat=6)
        self.imageDefaut("Bombe")
        self.puissance = puissance
        self.animations.play("Bombe", None, self.explosion)
        self.setZValue(0)

    def explosion(self):
        self.detruire()
        QSound.play("./sons/exploserb.wav")
        man = None
        for i, item in enumerate(self.scene.items()):
            if(type(item) == IA3):
                man = item
                man.now = man.now-1
        a = randint(0, 3)
        f = Flamme1(self.scene, self.x(), self.y(), a)
        b1 = True
        b2 = True
        b3 = True
        b4 = True
        for i in range(1, self.puissance+1):
            if self.x()+80*i < self.scene.width() and b1 == True:
                if(self.checkBlock(self.x()+80*i, self.y()) == True):
                    f = Flamme1(self.scene, self.x()+80*i, self.y(), a)
                else:
                    b1 = False
            if self.x()-80*i >= 0 and b2 == True:
                if(self.checkBlock(self.x()-80*i, self.y()) == True):
                    f = Flamme1(self.scene, self.x()-80*i, self.y(), a)
                else:
                    b2 = False
            if self.y()-80*i >= 0 and b3 == True:
                if(self.checkBlock(self.x(), self.y()-80*i) == True):
                    f = Flamme1(self.scene, self.x(), self.y()-80*i, a)
                else:
                    b3 = False
            if self.y()+80*i < self.scene.height() and b4 == True:
                if(self.checkBlock(self.x(), self.y()+80*i) == True):
                    f = Flamme1(self.scene, self.x(), self.y()+80*i, a)
                else:
                    b4 = False

    def checkBlock(self, x, y):
        pt = True
        for i, item in enumerate(self.scene.items()):
            if(type(item) == Block):
                bx = item.x()
                by = item.y()
                if bx == x and by == y:
                    pt = False
                    if item.can_Destroy == True:
                        item.detruire()
                        z = randint(0, 100)
                        if(z <= 10):
                            up = Booster(self.scene, bx+8, by+8)
                        elif(z <= 20):
                            up = Booster(self.scene, bx+8, by+8, "FlamePower")
        return pt

class Block(Objet):          # Création de différents blocks, cassables ou non
    def __init__(self, scene, x=0, y=0, blocktype="solidblock"):
        super().__init__(scene, x, y)
        self.animations.add("solidblock", ['Image/arbre.png'], non_stop=False)
        self.animations.add("explodableblock", ['Image/arbre_cassable.png'], non_stop=False)
        self.blocktype = blocktype
        self.imageDefaut(self.blocktype)
        self.can_Destroy = False
        if(blocktype == "explodableblock"):
            self.can_Destroy = True

class Rejouer(Objet):        # Permet de créer un bouton rejouer
    def __init__(self,scene,x=0,y=0):
        super().__init__(scene,x,y)
        self.animations.add("REnormal",["Image/Rejouer_Normal.png"],interval=1,non_stop = False)
        self.animations.add("REhover",["Image/Rejouer_Hover.png"],interval=1,non_stop = False)
        self.imageDefaut("REnormal")
        self.setAcceptHoverEvents(True)
        self.con=0

    def hoverEnterEvent(self, event):
        self.con=1
        self.animations.play("REhover", None)
        QSound.play("./sons/hover.wav")

    def hoverLeaveEvent(self,event):
        self.con=0
        self.animations.play("REnormal", None)

    def mousePressEvent(self,event):
        if self.con==1:
            python = sys.executable
            os.execl(python, python, * sys.argv)

app = QApplication([])
scene = AnimatedScene(1280, 720)
collision = gestionCollision(scene)
img = Image(scene, 0, 0, "Image/Fond.jpg")
b = unJoueur(scene, 180, 50)
a = deuxJoueurs(scene, 180, 100)
win = Window()
sys.exit(app.exec_())

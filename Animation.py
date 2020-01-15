#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import os
import sys
from random import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
import collections


DEBUG = False

class AnimatedScene(QGraphicsScene):   # Créé la fenêtre
    def __init__(self, width, height):
        super().__init__(0, 0, width, height)
        self.view = QGraphicsView(self)
        self.view.setFixedSize(1280, 720)           # Taille de la page (fixe)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)        # Règle un bug qui faisait apparaître des barres de navigations
        self.view.horizontalScrollBar().blockSignals(True)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.verticalScrollBar().blockSignals(True)
        self.view.show()

    def keyPressEvent(self, event):  # évènements clavier
        for item in self.items():
            item.keyPressEvent(event)

    def mousePressEvent(self,event):        # évènements souris
        for item in self.items():
            item.mousePressEvent(event)

class Message(QGraphicsItem):         # Permet d'afficher un message en grand au milieu de l'écran ( victoire / défaite )

    Item = collections.namedtuple("Item", ['message', 'seconds'])

    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.setX(0)
        self.setY(200)
        self.scene.addItem(self)
        self.items = []
        self.current_item = Message.Item("", 0)
        self.current_seconds = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_timer)
        self.timer.start(1000)
        self.setOpacity(1)
        self.setZValue(99999)

    def add(self, message, last_for_seconds=3, is_urgent=False):
        item = Message.Item(message=message, seconds=last_for_seconds)
        if is_urgent:
            self.items.insert(0, item)
        else:
            self.items.append(item)

    def check_timer(self):
        self.current_seconds += 1
        if self.current_seconds >= self.current_item.seconds:
            if not self.items:
                self.current_item = Message.Item("", 0)
            else:
                self.current_item = self.items.pop(0)
            self.current_seconds = 0
            self.update()

    def paint(self, painter, option, widget):
        if not self.current_item.message:
            return
        painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
        painter.setFont(QFont('Impact', 25))
        painter.drawRect(self.boundingRect())
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self.current_item.message)

    def boundingRect(self):
        return QRectF(10, 10, self.scene.view.width()-20, 50)

class Objet(QGraphicsItem):           # Permet de créer des objets (Personnages, flammes, boosters, bombes, IA, ..)
    def __init__(self, scene, x=0, y=0):
        super().__init__()
        self.animations = Animations(self.on_update_frame)   # Initialisation de la création d'un objet
        self.scene = scene
        self.scene.addItem(self)
        self.image = None
        self.setX(x)
        self.setY(y)
        self.collidable = True
        self.collision_rect = None

    def imageDefaut(self, animation_name, frame_index=0):    # Permet d'affecter à un objet une image qui le représentera
        self.image = self.animations.get_item(animation_name).get_static_frame(frame_index)

    def width(self):    # Largeur d'un obj
        return self.animations.max_width

    def height(self):   # Hauteur d'un obj
        return self.animations.max_height

    def paint(self, painter, option, widget):  # QPainter
        if self.image:
            painter.drawImage(0, 0, self.image)
        if not DEBUG:
            return
        pen = QPen(Qt.black, 1,Qt.DashDotLine)
        painter.setPen(pen)
        if self.collision_rect:
            painter.drawRect(self.collision_rect.x(), self.collision_rect.y(),
                             self.collision_rect.width(), self.collision_rect.height())
        else:
            painter.drawRect(0, 0, self.width(), self.height())

    def boundingRect(self):         # Rectangle autour d'un objet
        return QRectF(0, 0, self.width(), self.height())

    def on_update_frame(self, frame):
        self.image = frame
        self.update()

    @staticmethod
    def point_inside_rect(point, rect):
        return rect.x() < point.x() < rect.x() + rect.width() and rect.y() < point.y() < rect.y() + rect.height()

    def pointCollision(self, other):
        if self.collision_rect:
            self_left, self_top = self.x() + self.collision_rect.x(), self.y() + self.collision_rect.y()
            self_right, self_bottom = self_left + self.collision_rect.width(), self_top + self.collision_rect.height()
        else:
            self_left, self_top = self.x(), self.y()
            self_right, self_bottom = self.x() + self.width(), self.y() + self.height()

        if other.collision_rect:
            other_left, other_top = other.x() + other.collision_rect.x(), other.y() + other.collision_rect.y()
            other_right, other_bottom = other_left + other.collision_rect.width(), \
                                        other_top + other.collision_rect.height()
        else:
            other_left, other_top = other.x(), other.y()
            other_right, other_bottom = other_left + other.width(), other_top + other.height()
        return self_left < other_right and self_right > other_left and \
               self_top < other_bottom and self_bottom > other_top

    def collision(self, other):  # Initialisation de la fonction qui gère les collisions d'objets avec d'autres
        pass

    def detruire(self):   # Détruit un objet
        if self in self.scene.items():
            self.scene.removeItem(self)

class gestionCollision:               # Permet de vérifier les collisions entre chaques objets
    def __init__(self, scene):
        self.scene = scene
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_collisions)
        self.timer.start(50)

    def check_collisions(self):
        for i, item1 in enumerate(self.scene.items()):
            for item2 in self.scene.items()[i+1:]:
                if not isinstance(item1, Objet) or not isinstance(item2, Objet):
                    continue
                if not item1.collidable and not item2.collidable:
                    continue
                if item1.pointCollision(item2):
                    if item1.collidable:
                        item1.collision(item2)
                    if item2.collidable:
                        item2.collision(item1)

class Animations:
    def __init__(self, on_update_frame):
        self.animation_dict = {}
        self.is_playing = False
        self.on_update_frame = on_update_frame
        self.completion_callback = None
        self.max_width = 0
        self.max_height = 0

    def add(self, name, image_file_names, interval=500, repeat=1, horizontal_flip=False,
            vertical_flip=False, non_stop=True):
        frames = Frames(image_file_names, on_timeout=self.update_frame, interval=interval, repeat=repeat,
                        horizontal_flip=horizontal_flip, vertical_flip=vertical_flip, non_stop=non_stop)
        self.animation_dict[name] = frames
        if frames.max_width > self.max_width:
            self.max_width = frames.max_width
        if frames.max_height > self.max_height:
            self.max_height = frames.max_height

    def get_item(self, animation_name):
        return self.animation_dict[animation_name]

    def play(self, name, on_transition=None, on_completion=None):
        frames = self.animation_dict[name]
        if not self.is_playing:
            if on_transition:
                frames.set_transition_callback(on_transition)
            if on_completion:
                self.completion_callback = on_completion
            frames.start()
            self.is_playing = True

    def update_frame(self, frame):
        if not frame:
            self.is_playing = False
            if self.completion_callback:
                self.completion_callback()
                self.completion_callback = None
        else:
            self.on_update_frame(frame)                    # Frames et Animations permettent de gérer toutes les animations, sprites des objets

class Frames:
    def __init__(self, img_file_paths, on_timeout=None, interval=500, repeat=1,
                 horizontal_flip=False, vertical_flip=False, non_stop=True):
        self.frames = []
        self.max_width = 0
        self.max_height = 0
        for file_path in img_file_paths:
            img = QImage(file_path)
            if img.height() > self.max_height:
                self.max_height = img.height()
            if img.width() > self.max_width:
                self.max_width = img.width()
            if horizontal_flip or vertical_flip:
                img = img.mirrored(horizontal_flip, vertical_flip)
            self.frames.append(img)
        self.frames *= repeat
        self.index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        self.interval = interval
        self.timeout_callback = on_timeout
        self.non_stop = non_stop
        self.transition_callback = None
        self.completion_callback = None

    def set_transition_callback(self, callback):
        self.transition_callback = callback

    def set_completion_callback(self, callback):
        self.completion_callback = callback

    def start(self):
        if not self.timer.isActive():
            self.index = 0
            self.timer.start(self.interval)
        if self.non_stop:
            self.timeout()

    def next(self):
        if self.index == len(self.frames):
            if self.completion_callback:
                self.completion_callback()
            self.index = 0
            return None
        frame = self.frames[self.index]
        self.index += 1
        if self.transition_callback:
            self.transition_callback()
        return frame

    def timeout(self):
        frame = self.next()
        self.timeout_callback(frame)
        if not frame:
            self.timer.stop()

    def get_static_frame(self, frame_index=0):
        return self.frames[frame_index]

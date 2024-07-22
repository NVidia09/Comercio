import os
import sys

import cv2
import pygame

class DNI_captura:
    def __init__(self, codfactura):
        self.codfactura = codfactura
        pygame.mixer.init()
        pygame.mixer.music.load("C:\Cursos\Python\Cursos\Comercio\Comercio\Conexion\sonido_scaner.mp3")

    def play_sound(self):
        pygame.mixer.music.play()

    def capture(self):
        cap = cv2.VideoCapture(0)
        photo_count = 0
        cuadro = 100
        doc=0

        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        center_x = int(width / 2)
        center_y = int(height / 2)

        start_x = center_x - 200
        start_y = center_y - 150
        end_x = center_x + 200
        end_y = center_y + 150

        while cap.isOpened():
            success, frame = cap.read()

            cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

            cv2.putText(frame, "PRESIONE 'c' PARA CAPTURAR", (200, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Definir la ruta base dependiendo de si se ejecuta como .exe o .py
            if getattr(sys, 'frozen', False):
                # Ejecutado como un archivo .exe
                basedir = sys._MEIPASS
            else:
                # Ejecutado como un archivo .py
                basedir = os.path.dirname(os.path.abspath(__file__))

            # Construir la ruta al directorio Despacho
            despacho_dir = os.path.join(basedir, "Despacho")

            # Asegurarse de que el directorio Despacho existe
            if not os.path.exists(despacho_dir):
                os.makedirs(despacho_dir)

            cv2.imshow('scanner', frame)

            key = cv2.waitKey(1) & 0xFF

            if key in [ord('c'), ord('C')] and photo_count < 2:
                photo_count += 1
                if photo_count == 1:
                    # cv2.imwrite(f"Despacho/FacturaN-{self.codfactura}_frente.png", frame)
                    file_path = os.path.join(despacho_dir,
                                             f"FacturaN-{self.codfactura}_frente.png")
                    cv2.imwrite(file_path, frame)
                else:
                    file_path = os.path.join(
                        despacho_dir, f"FacturaN-{self.codfactura}_dorso.png")
                    cv2.imwrite(file_path, frame)
                # else:
                #     cv2.imwrite(f"Despacho/FacturaN-{self.codfactura}_dorso.png", frame)
                self.play_sound()

            elif key in [ord('q'), ord('Q')] or photo_count == 2:
                break

        cap.release()
        cv2.destroyAllWindows()
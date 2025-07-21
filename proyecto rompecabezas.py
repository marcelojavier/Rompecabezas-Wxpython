import wx
import random
import os
from PIL import Image

class PiezaRompecabezas:
    def __init__(self, imagen, posicion_original, posicion_actual):
        self.imagen = imagen
        self.posicion_original = posicion_original
        self.posicion_actual = posicion_actual
        self.es_correcta = False

class JuegoRompecabezas(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.tamaño_pieza = 150  # Tamaño de cada pieza
        self.filas = 3
        self.columnas = 3
        self.piezas = []
        self.pieza_seleccionada = None
        self.posicion_vacia = (2, 2)  # Última posición está vacía
        self.imagen_original = None
        
        # Cargar la imagen
        self.cargar_imagen()
        
        # Crear las piezas
        self.crear_piezas()
        
        # Mezclar las piezas
        self.mezclar_piezas()
        
        # Configurar eventos
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        
        # Configurar el tamaño del panel
        self.SetMinSize((self.tamaño_pieza * self.columnas, self.tamaño_pieza * self.filas))

    def cargar_imagen(self):
        """Carga y redimensiona la imagen del rompecabezas"""
        ruta_imagen = os.path.join(os.path.dirname(__file__), "descarga.jpeg")
        
        if not os.path.exists(ruta_imagen):
            wx.MessageBox("No se encontró la imagen 'descarga.jpeg'", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        try:
            # Cargar con PIL para redimensionar
            pil_imagen = Image.open(ruta_imagen)
            
            # Redimensionar a un tamaño múltiplo de 3
            tamaño_total = self.tamaño_pieza * 3
            pil_imagen = pil_imagen.resize((tamaño_total, tamaño_total), Image.Resampling.LANCZOS)
            
            # Convertir a wxPython
            wx_imagen = wx.Image(tamaño_total, tamaño_total)
            wx_imagen.SetData(pil_imagen.convert('RGB').tobytes())
            
            self.imagen_original = wx_imagen.ConvertToBitmap()
            
        except Exception as e:
            wx.MessageBox(f"Error al cargar la imagen: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def crear_piezas(self):
        """Crea las 8 piezas del rompecabezas (la 9na está vacía)"""
        if not self.imagen_original:
            return
            
        self.piezas = []
        
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if (fila, columna) == self.posicion_vacia:
                    continue  # Saltamos la posición vacía
                
                # Extraer la porción de imagen para esta pieza
                x = columna * self.tamaño_pieza
                y = fila * self.tamaño_pieza
                
                # Crear un bitmap temporal para extraer la región
                imagen_dc = wx.MemoryDC()
                imagen_dc.SelectObject(self.imagen_original)
                
                pieza_bitmap = wx.Bitmap(self.tamaño_pieza, self.tamaño_pieza)
                pieza_dc = wx.MemoryDC()
                pieza_dc.SelectObject(pieza_bitmap)
                
                pieza_dc.Blit(0, 0, self.tamaño_pieza, self.tamaño_pieza, imagen_dc, x, y)
                
                pieza_dc.SelectObject(wx.NullBitmap)
                imagen_dc.SelectObject(wx.NullBitmap)
                
                # Crear la pieza
                pieza = PiezaRompecabezas(
                    pieza_bitmap,
                    (fila, columna),  # Posición original
                    (fila, columna)   # Posición actual
                )
                
                self.piezas.append(pieza)

    def mezclar_piezas(self):
        """Mezcla las piezas del rompecabezas"""
        # Realizar múltiples movimientos aleatorios
        for _ in range(200):
            self.mover_pieza_aleatoria()

    def mover_pieza_aleatoria(self):
        """Mueve una pieza aleatoria hacia la posición vacía si es posible"""
        fila_vacia, col_vacia = self.posicion_vacia
        
        # Posiciones adyacentes a la vacía
        movimientos_posibles = [
            (fila_vacia - 1, col_vacia),  # Arriba
            (fila_vacia + 1, col_vacia),  # Abajo
            (fila_vacia, col_vacia - 1),  # Izquierda
            (fila_vacia, col_vacia + 1)   # Derecha
        ]
        
        # Filtrar movimientos válidos
        movimientos_validos = [
            (f, c) for f, c in movimientos_posibles
            if 0 <= f < self.filas and 0 <= c < self.columnas
        ]
        
        if movimientos_validos:
            pos_a_mover = random.choice(movimientos_validos)
            self.intercambiar_con_vacia(pos_a_mover)

    def obtener_pieza_en_posicion(self, fila, columna):
        """Obtiene la pieza que está en una posición específica"""
        for pieza in self.piezas:
            if pieza.posicion_actual == (fila, columna):
                return pieza
        return None

    def intercambiar_con_vacia(self, posicion):
        """Intercambia una pieza con la posición vacía"""
        pieza = self.obtener_pieza_en_posicion(posicion[0], posicion[1])
        if pieza:
            pieza.posicion_actual = self.posicion_vacia
            self.posicion_vacia = posicion
            return True
        return False

    def on_click(self, event):
        """Maneja los clics del mouse"""
        x, y = event.GetPosition()
        
        # Calcular qué celda fue clickeada
        columna = x // self.tamaño_pieza
        fila = y // self.tamaño_pieza
        
        if 0 <= fila < self.filas and 0 <= columna < self.columnas:
            # Verificar si es adyacente a la posición vacía
            fila_vacia, col_vacia = self.posicion_vacia
            
            if ((abs(fila - fila_vacia) == 1 and columna == col_vacia) or
                (abs(columna - col_vacia) == 1 and fila == fila_vacia)):
                
                # Intercambiar con la posición vacía
                if self.intercambiar_con_vacia((fila, columna)):
                    self.Refresh()
                    
                    # Verificar si se completó el rompecabezas
                    if self.verificar_victoria():
                        wx.MessageBox("¡Felicitaciones! Has completado el rompecabezas", 
                                    "Victoria", wx.OK | wx.ICON_INFORMATION)

    def verificar_victoria(self):
        """Verifica si el rompecabezas está completo"""
        for pieza in self.piezas:
            if pieza.posicion_actual != pieza.posicion_original:
                return False
        
        # Verificar que la posición vacía esté en el lugar correcto
        return self.posicion_vacia == (2, 2)

    def on_paint(self, event):
        """Dibuja el rompecabezas"""
        dc = wx.PaintDC(self)
        self.dibujar_rompecabezas(dc)

    def dibujar_rompecabezas(self, dc):
        """Dibuja todas las piezas del rompecabezas"""
        # Limpiar el fondo
        dc.SetBackground(wx.Brush(wx.Colour(240, 240, 240)))
        dc.Clear()
        
        # Dibujar cada pieza
        for pieza in self.piezas:
            fila, columna = pieza.posicion_actual
            x = columna * self.tamaño_pieza
            y = fila * self.tamaño_pieza
            
            dc.DrawBitmap(pieza.imagen, x, y)
            
            # Dibujar borde
            dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 2))
            dc.SetBrush(wx.Brush(wx.Colour(255, 255, 255), wx.BRUSHSTYLE_TRANSPARENT))
            dc.DrawRectangle(x, y, self.tamaño_pieza, self.tamaño_pieza)
        
        # Dibujar la posición vacía
        fila_vacia, col_vacia = self.posicion_vacia
        x_vacia = col_vacia * self.tamaño_pieza
        y_vacia = fila_vacia * self.tamaño_pieza
        
        dc.SetBrush(wx.Brush(wx.Colour(200, 200, 200)))
        dc.DrawRectangle(x_vacia, y_vacia, self.tamaño_pieza, self.tamaño_pieza)

    def on_resize(self, event):
        """Maneja el redimensionamiento de la ventana"""
        self.Refresh()
        event.Skip()

class VentanaRompecabezas(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Rompecabezas de 9 Piezas", size=(500, 550))
        
        # Crear el panel principal
        self.panel = JuegoRompecabezas(self)
        
        # Crear la barra de menú
        self.crear_menu()
        
        # Centrar la ventana
        self.Center()

    def crear_menu(self):
        """Crea la barra de menú"""
        menubar = wx.MenuBar()
        
        # Menú Juego
        menu_juego = wx.Menu()
        item_nuevo = menu_juego.Append(wx.ID_NEW, "&Nuevo Juego\tCtrl+N", "Comenzar un nuevo juego")
        menu_juego.AppendSeparator()
        item_salir = menu_juego.Append(wx.ID_EXIT, "&Salir\tCtrl+Q", "Salir del juego")
        
        # Menú Ayuda
        menu_ayuda = wx.Menu()
        item_acerca = menu_ayuda.Append(wx.ID_ABOUT, "&Acerca de", "Información sobre el juego")
        
        menubar.Append(menu_juego, "&Juego")
        menubar.Append(menu_ayuda, "&Ayuda")
        
        self.SetMenuBar(menubar)
        
        # Vincular eventos
        self.Bind(wx.EVT_MENU, self.on_nuevo_juego, item_nuevo)
        self.Bind(wx.EVT_MENU, self.on_salir, item_salir)
        self.Bind(wx.EVT_MENU, self.on_acerca_de, item_acerca)

    def on_nuevo_juego(self, event):
        """Inicia un nuevo juego"""
        self.panel.mezclar_piezas()
        self.panel.Refresh()

    def on_salir(self, event):
        """Sale del juego"""
        self.Close()

    def on_acerca_de(self, event):
        """Muestra información sobre el juego"""
        info = wx.adv.AboutDialogInfo()
        info.SetName("Rompecabezas de 9 Piezas")
        info.SetVersion("1.0")
        info.SetDescription("Un juego de rompecabezas deslizante de 9 piezas")
        info.SetWebSite("https://github.com")
        info.AddDeveloper("Tu nombre aquí")
        
        wx.adv.AboutBox(info)

class AplicacionRompecabezas(wx.App):
    def OnInit(self):
        ventana = VentanaRompecabezas()
        ventana.Show()
        return True

if __name__ == "__main__":
    app = AplicacionRompecabezas()
    app.MainLoop()
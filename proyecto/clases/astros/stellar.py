#IMPORTACIONES
import os
from datetime import datetime
from astropy.time import Time
import math
from astropy.coordinates import Angle
import pandas as pd
import numpy as np 
from timezonefinder import TimezoneFinder
from PIL import Image
from PIL import ImageDraw, ImageFont
from skyfield.api import load
#import blog.site.classes.astros.construir_imagen as ci
#import blog.site.classes.astros.destruir_imagen as di
#import blog.site.classes.astros.conexion as conexion
#import blog.site.classes.astros.encriptacion as encriptacion
#import blog.site.classes.astros.CodigosQR as CodigosQR
import svgwrite
#################################################  PARAMETROS ###################################################
#Parámetros en este caso "Constantes o fijos", dados por el testeador
#Posteriormente para recibir datos del usuario

class Astros:
    def __init__(self,latitud,longitud,año,mes,dia,hora,mins,seg):
        self.LAT_grados=latitud+" degrees"
        self.LONG_grados=longitud+" degrees"
        self.fecha_año=año
        self.fecha_mes=mes
        self.fecha_dia=dia
        self.fecha_hora=hora
        self.fecha_min=mins
        self.fecha_seg=seg
        self.anchura=550
        self.altura=550
        self.LMST_grados=""
        self.earth=""
        self.db_estrellas=""
        self.db_constelaciones=""
        self.db_nombres_const=""
        self.dwg = svgwrite.Drawing(profile='tiny', size=(u'550px',u'550px'))

############################FUNCIONES CALCULO###########################################
########################################################80411305  23/07/2019################################

#FUNCIÓN PARA OBTENER LA HORA SIDERAL MEDIA LOCAL

    def decdeg2dms(self,dd):
      is_positive = dd >= 0
      dd = abs(dd)
      minutes,seconds = divmod(dd*3600,60)
      degrees,minutes = divmod(minutes,60)
      degrees = degrees if is_positive else -degrees
      return (str(int(degrees))+":"+str(int(minutes))+":"+str(int(seconds))+" degrees")

    def get_LMST(self,latitud,longitud):
        ut1= datetime(self.fecha_año,self.fecha_mes,self.fecha_dia,self.fecha_hora,self.fecha_min,self.fecha_seg)   
        ut1=Time(ut1, scale='utc',location=(self.LONG_grados,self.LAT_grados))
        tf = TimezoneFinder()
        tz=tf.timezone_at(lng=longitud, lat=latitud)
        data=np.genfromtxt('timeZones.txt',delimiter='\t',names=True,dtype=None,encoding='utf-8')
        indice = np.where(data['TimeZoneId'] == tz)
        if(tz==None):
            print("NO EXISTE ZONA HORARIA")
            y=0
        else:
            y=data[indice][0][3]*15
        print(y)
        self.LMST_grados=Angle(ut1.sidereal_time('mean')).degree-y
        print(self.LMST_grados)

#PARA CALCULAR MULTIPLICADOR PARA EL RADIO CUANDO SE DIBUJA
    def calc_rad(self,mag): 
        if mag>=5:
            return float(1)
        elif mag>=4:
            return float(2)
        elif mag>=3:
            return float(3)
        elif mag>=2:
            return float(5)
        elif mag>=1:
            return float(6)
        elif mag>=0:
            return float(7)
        elif mag>=-1:
            return float(8)
        else:
            return float(10)

#PARA OBTERNER LA ALTITUD
    def get_ALT(self,DEC_grados,LATI_grados,HA):
        ALT=math.asin(math.sin(DEC_grados)*math.sin(Angle(LATI_grados).rad)+math.cos(DEC_grados)*math.cos(Angle(LATI_grados).rad)*math.cos(self.sex_a_rad(HA)))
        return ALT

#PARA OBTENER LA AZIMUT
    def get_AZ(self,DEC_grados,ALT,LATI_grados,HA):
        A=math.acos((math.sin(DEC_grados)-math.sin(ALT)*math.sin(Angle(LATI_grados).rad))/(math.cos(ALT)*math.cos(Angle(LATI_grados).rad)))
        con=math.sin(self.sex_a_rad(HA))
        if con < 0:
            AZ=A
        else:
            AZ=2*math.pi-A
        return AZ    

#PARA CONVERTIR DE SEXAGESIMALES A RADIANES 
    def sex_a_rad(self,x):
        return x*math.pi/180

    def rotar_pos(self,x,y):
        return (self.anchura-x,self.altura-y)
    
#PARA HALLAR COORDENADAS ANTES DE DIBUJAR
    def hallar_coordenadas(self,altitud,azimut,mag=0):
        radio= 0.47*self.anchura*math.tan((math.pi/4)-altitud/2)
        cord_x = math.sin(azimut)*radio + mag + self.anchura/2
        cord_y = math.cos(azimut)*radio + mag + self.altura/2
        return cord_x, cord_y

########################################################################################
######################################### DATOS ########################################
    def iniciar_bases(self):
        self.db_estrellas= pd.read_excel('proyecto/clases/astros/Estrellitas.xlsx') #LECTURA DE BD DE ESTRELLAS
        self.db_constelaciones= pd.read_excel('proyecto/clases/astros/const1.xlsx') #LECTURA DE BD DE CONSTELACIONES
        self.db_nombres_const= pd.read_excel("proyecto/clases/astros/nombres.xlsx") #LECTURA DE BD DE NOMBRES DE LAS CONSTELACIONES
        print("EOO")
#######################PARA DIBUJAR ESTRELLA###################################3  
    def dibujar_estrella(self,altitud, azimut, mag):
        if altitud>=0:
            x,y=self.hallar_coordenadas(altitud,azimut,-mag)
            x1,y1=self.hallar_coordenadas(altitud,azimut,+mag)
            x,y=self.rotar_pos(x,y)
            x1,y1=self.rotar_pos(x1,y1)
            self.dwg.add(self.dwg.circle(center=((x+x1)/2,(y+y1)/2), r=(x-x1)/6,fill='white'))

############################## DIBUJAR PLANETAS ##########################################
    def graficar_planeta(self,plnt,t,nombre):
        long=len(nombre)
        position = self.earth.at(t).observe(plnt)
        ra, dec, distancia = position.radec()
        ra=ra._degrees
        dec=str(dec.degrees)+"d"
        dec=Angle(dec).rad
        HA=self.LMST_grados-ra
        altitud_planeta,azimut_planeta=self.get_alt_az(dec,HA)

        if altitud_planeta>=0:
            x,y=self.hallar_coordenadas(altitud_planeta,azimut_planeta,-10)
            x1,y1=self.hallar_coordenadas(altitud_planeta,azimut_planeta,+10)
            x,y=self.rotar_pos(x,y) #rotacionesa
            x1,y1=self.rotar_pos(x1,y1)
            if nombre == "Sol":
                self.dwg.add(self.dwg.image('https://projectostars.herokuapp.com/static/'+nombre+'.svg',((x+x1)/2-10,(y+y1)/2-10),(20,20)))
            else:
                self.dwg.add(self.dwg.image('https://projectostars.herokuapp.com/static/'+nombre+'.svg',((x+x1)/2-7.5,(y+y1)/2-7.5),(15,15)))
            self.dwg.add(self.dwg.text(nombre, insert=(x1, y1), fill='white',font_size=9, font_family="Myriad",font_weight="bold",font_style="oblique"))
##########################OBTENER ALTITUD AZIMUT ###################################3
    def get_alt_az(self,declinacion,ascencion_recta):
        altitud=self.get_ALT(declinacion,self.LAT_grados,ascencion_recta)
        azimut=self.get_AZ(declinacion,altitud,self.LAT_grados,ascencion_recta)
        return altitud,azimut


####################################### DIBUJAR - ESTRELLAS #############################    
    def plotear_estrellas(self):
        self.dwg
        self.dwg.viewbox(0,0,self.anchura,self.altura)
        self.dwg.add(self.dwg.rect(insert=(0, 0), size=(self.anchura, self.altura),fill='white')) ####RECTANGULO - FONDO
        self.dwg.add(self.dwg.circle(center=(self.anchura/2,self.altura/2), r=self.anchura/2, fill=svgwrite.rgb(24, 24, 30))) #### CIRCULO - FONDO
        self.db_estrellas['MAG']=self.db_estrellas['MAG'].apply(self.calc_rad)
        self.db_estrellas['RA(sex)']=self.LMST_grados-self.db_estrellas['RA(sex)']

        #Graficando estrellas....
        for index,row in self.db_estrellas.iterrows(): # FUNCION PLOTEO ESTRELLAS
            ALT,AZ=self.get_alt_az(row['DEC(rad)'],row['RA(sex)'])
            self.dibujar_estrella(ALT, AZ, row['MAG'])

################################# DIBUJAR - CONSTELACIONES ###############################
    def plotear_constelaciones(self):
        
        #self.grafico = ImageDraw.Draw(self.imagen_principal)
        self.db_constelaciones['RA_INI(sex)']=self.LMST_grados-self.db_constelaciones['RA_INI(sex)']
        self.db_constelaciones['RA_FIN(sex)']=self.LMST_grados-self.db_constelaciones['RA_FIN(sex)']
        print("Dibujando ConstO")
        #Graficando constelaciones....
        for index,row in self.db_constelaciones.iterrows():
            ALT1,AZ1=self.get_alt_az(row['DEC_INI(rad)'],row['RA_INI(sex)'])
            ALT2,AZ2=self.get_alt_az(row['DEC_FIN(rad)'],row['RA_FIN(sex)'])
            if ALT1>=-0.05 and ALT2>=-0.05 and AZ1 >=-0.05 and AZ2 >=-0.05 : #4 AND
                x,y=self.hallar_coordenadas(ALT1,AZ1)
                x1,y1=self.hallar_coordenadas(ALT2,AZ2)
                x,y=self.rotar_pos(x,y)
                x1,y1=self.rotar_pos(x1,y1)
                
                self.dwg.add(self.dwg.line((x1,y1),(x,y), stroke='white',stroke_width = '0.2'))

################################ NOMBRES DE CONSTELACIONES ##########################

        self.db_nombres_const['RA(sex)']=self.LMST_grados-self.db_nombres_const['RA(sex)']
        for index,row in self.db_nombres_const.iterrows():
            ALT3,AZ3=self.get_alt_az(row['DEC(rad)'],row['RA(sex)'])
            if ALT3-0.05>=0 and AZ3-0.05>=0: #####################AGREGADO CONDICION 
                x,y=self.hallar_coordenadas(ALT3,AZ3)
                #if (math.sqrt(pow(abs(self.anchura/2-x),2)+pow(abs(self.altura/2-y),2))<=self.altura/2):
                nombre=row['NOMBRE']
                x,y=self.rotar_pos(x, y)
                self.dwg.add(self.dwg.text(nombre, insert=(x-len(nombre)*1, y), fill='white', font_size=8,font_family="Calibri",font_style="oblique"))
                ##### LOS PARAMETROS DE GRAFICO.TEXT ERAN( X,Y )  AHORA PARA LA ROTACION ES (ANCHURA-X, ALTURA -Y)
    
################################### PARA PLANETAS ###################################
    def plotear_planetas(self):
        planetas = load('de421.bsp') #Cargando planetas
        self.earth, venus, sun, mercury,neptune,mars,saturn,jupyter,uranus,moon = planetas['earth'], planetas['venus'], planetas['sun'],planetas[1], planetas[8], planetas['mars'], planetas[6], planetas[5], planetas[7], planetas['moon']
        ts = load.timescale()
        t = ts.utc(self.fecha_año,self.fecha_mes,self.fecha_dia,self.fecha_hora,self.fecha_min,self.fecha_seg)

        self.graficar_planeta(venus,t,'Venus')
        self.graficar_planeta(mercury,t,'Mercurio')
        self.graficar_planeta(mars,t,'Marte')
        self.graficar_planeta(saturn,t,'Saturno')
        self.graficar_planeta(jupyter,t,'Jupiter')
        self.graficar_planeta(neptune,t,'Neptuno')
        self.graficar_planeta(sun,t,'Sol')
        self.graficar_planeta(moon,t,'Luna')
        self.graficar_planeta(uranus,t,'Urano')
    
    def guardar_imagen(self,nombre):
        self.dwg.filename='proyecto/static/images/'+nombre+'.svg'
        self.dwg.save()
        #self.imagen_principal.save('blog/media/'+nombre+'.jpg') ######### VACIO NO SE USA
        #print (time() - tiempo_inicial)

#FUNCIÓN DEL CODIGO QR, CREAR IMAGEN QR + ESTRELLAS    
def appAstrosQR(latitud,longitud,año,mes,dia,hora,mins,seg):
    astro=Astros(latitud,longitud,año,mes,dia,hora,mins,seg)
    astro.get_LMST(float(latitud),float(longitud))
    astro.iniciar_bases()
    astro.plotear_estrellas()
    astro.plotear_constelaciones()
    astro.plotear_planetas()
    #contenido=latitud+"/"+longitud+"/"+str(año)+"/"+str(mes)+"/"+str(dia)+"/"+str(hora)+"/"+str(mins)+"/"+str(seg)
    #contenido_bytes=encriptacion.encriptar(contenido)
    #CodigosQR.generarQR(contenido_bytes,"ejemplo")
    astro.guardar_imagen("astros"+latitud+"_"+str(dia)+"_"+str(mes)+"_"+str(año)+"_"+str(hora)+"_"+str(mins))




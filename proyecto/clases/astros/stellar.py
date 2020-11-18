#IMPORTACIONES
import os
from datetime import datetime
from astropy.time import Time
from astropy import units as u
import math
from astropy.coordinates import Angle
import pandas as pd
import numpy as np 
from timezonefinder import TimezoneFinder
from PIL import Image
from PIL import ImageDraw, ImageFont
from skyfield.api import load,utc

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
    def __init__(self,latitud,longitud,fecha_hora,anchura=550,altura=550):
        self.latitud=latitud
        self.longitud=longitud
        self.LAT_grados=latitud+" degrees"
        self.LONG_grados=longitud+" degrees"
        self.fecha_hora=fecha_hora
        self.anchura=anchura
        self.altura=altura
        self.LMST_grados=""
        self.earth=""
        self.db_estrellas=""
        self.db_constelaciones=""
        self.db_nombres_const=""
        self.dwg = svgwrite.Drawing(profile='tiny', size=(u'550px',u'550px'))

############################FUNCIONES CALCULO###########################################

    def get_altaz_stars(self):
        return self.db_estrellas[['ALT','AZ']]
    
    def get_altaz_cons(self):
        return self.db_estrellas[['ALT','AZ']]
    
    def decdeg2dms(self,dd):
      is_positive = dd >= 0
      dd = abs(dd)
      minutes,seconds = divmod(dd*3600,60)
      degrees,minutes = divmod(minutes,60)
      degrees = degrees if is_positive else -degrees
      return (str(int(degrees))+":"+str(int(minutes))+":"+str(int(seconds))+" degrees")

    def get_LMST(self,latitud,longitud): #HORA SIDERAL LOCAL
        #ut1= datetime(self.fecha_año,self.fecha_mes,self.fecha_dia,self.fecha_hora,self.fecha_min,self.fecha_seg)   
        ut1=Time(self.fecha_hora, scale='utc',location=(self.LONG_grados,self.LAT_grados))
        tf = TimezoneFinder()
        tz=tf.timezone_at(lng=longitud, lat=latitud)
        data=np.genfromtxt('timeZones.txt',delimiter='\t',names=True,dtype=None,encoding='utf-8')
        indice = np.where(data['TimeZoneId'] == tz)
        if(tz==None):
            print("NO EXISTE ZONA HORARIA")
            y=0
        else:
            y=data[indice][0][3]*15
        self.LMST_grados=Angle(ut1.sidereal_time('mean'),unit=u.deg).rad-y*math.pi/180
        


    def calc_rad(self,mag): #PARA CALCULAR MULTIPLICADOR PARA EL RADIO CUANDO SE DIBUJA
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
        
        
    def hallar_coordenadas(self,altitud,azimut,mag=0):
        radio= 0.47*self.anchura*math.tan((math.pi/4)-altitud/2)
        cord_x = math.sin(azimut)*radio + mag + self.anchura/2
        cord_y = math.cos(azimut)*radio + mag + self.altura/2
        return cord_x, cord_y

    def get_alt_az(self,declinacion,ascencion_recta):
        #ALT and AZ para planetas (Version 1.0)
        altitud=self.get_ALT_v1(declinacion,self.LAT_grados,ascencion_recta)
        azimut=self.get_AZ_v1(declinacion,altitud,self.LAT_grados,ascencion_recta)
        return altitud,azimut
    
    #PARA OBTERNER LA ALTITUD
    def get_ALT_v1(self,DEC_grados,LATI_grados,HA):
        ALT=math.asin(math.sin(DEC_grados)*math.sin(Angle(LATI_grados).rad)+math.cos(DEC_grados)*math.cos(Angle(LATI_grados).rad)*math.cos(HA))
        return ALT

#PARA OBTENER LA AZIMUT
    def get_AZ_v1(self,DEC_grados,ALT,LATI_grados,HA):
        A=math.acos((math.sin(DEC_grados)-math.sin(ALT)*math.sin(Angle(LATI_grados).rad))/(math.cos(ALT)*math.cos(Angle(LATI_grados).rad)))
        con=math.sin(HA)
        if con < 0:
            AZ=A
        else:
            AZ=2*math.pi-A
        return AZ    

    def get_ALT(self,DEC,LAT,HA):
        #@Info: Obtiene Altitud de acuerdo a la declinacion(DEC) y angulo horario(HA)
        #@Params DEC(pd.Series,radianes) - ALT(pd.Series,radianes) - LAT(int/float, radianes) - HA(pd.Series,radianes)
        #@Output: ALT(pd.Series,radianes)
        ALT=np.arcsin(np.sin(DEC)*math.sin(math.radians(LAT))+np.cos(DEC)*math.cos(math.radians(LAT))*np.cos(HA))
        return ALT


    def get_AZ(self,DEC,ALT,LAT,HA):
        #@Info: Obtiene Azimut a la declinacion(DEC) y angulo horario(HA)
        #@Params DEC(pd.Series,radianes) - ALT(pd.Series,radianes) - LAT(int/float, radianes) - HA(pd.Series,radianes)
        #@Output: AZ(pd.Series,radianes)
        A=np.arccos((np.sin(DEC)-np.sin(ALT)*math.sin(math.radians(LAT)))/(np.cos(ALT)*math.cos(math.radians(LAT))))
        HA=np.sin(HA)
        AZ = A.where(HA<0,2*math.pi-A)
        return AZ 

    def rotar_pos_x(self,serie):
        return (self.anchura-serie)
    
    def rotar_pos_y(self,df,name):
        return self.altura-y[name]

    def sex_a_rad(self,x):#PARA CONVERTIR DE SEXAGESIMALES A RADIANES
        return x*math.pi/180

    def rotar_pos(self,x,y):
        #Retorna puntos para graficar el mapa rotado
        return (self.anchura-x,self.altura-y)
    

    def hallar_coordenadasX(self,altitud,azimut,mag=0):
        #@Info:Retorna una Serie(pandas) con las coordenadas X 
        #@Params ALT(pd.Series) - AZ(pd.Series) - MAG(pd.Series)
        #@Output: cord_x(pd.Series,radianes)
        radio= 0.47*self.anchura*np.tan((math.pi/4)-altitud/2)
        cord_x =np.sin(azimut)*radio + mag + self.anchura/2
        return cord_x

    def hallar_coordenadasY(self,altitud,azimut,mag=0):
        #@Info:Retorna una Serie(pandas) con las coordenadas Y
        #@Params ALT(pd.Series) - AZ(pd.Series) - MAG(pd.Series)
        #@Output: cord_y(pd.Series,radianes)
        radio= 0.47*self.anchura*np.tan((math.pi/4)-altitud/2)
        cord_y = np.cos(azimut)*radio + mag + self.altura/2
        return cord_y

########################################################################################
######################################### DATOS ########################################
    def read_databases(self):
        #@Info:
        self.db_estrellas= pd.read_excel('proyecto/clases/astros/Estrellitas.xlsx') #LECTURA DE BD DE ESTRELLAS
        self.db_constelaciones= pd.read_excel('proyecto/clases/astros/const1.xlsx') #LECTURA DE BD DE CONSTELACIONES
        self.db_nombres_const= pd.read_excel("proyecto/clases/astros/nombres.xlsx") #LECTURA DE BD DE NOMBRES DE LAS CONSTELACIONES
        
        

    def draw_stars(self,stars): 
        #@Info:Dibuja estrellas a partir de un dataframe
        #@Params: stars(pd.Dataframe de estrellas que contiene columnas de Altitud(ALT,radianes), Azimut(AZ,radianes) y Radio(int/float))
        #Output: None - Grafica estrellas
        s1=self.hallar_coordenadasX(stars['ALT'],stars['AZ'],-stars.radio)
        s2=self.hallar_coordenadasY(stars['ALT'],stars['AZ'],-stars.radio)
        s3=self.hallar_coordenadasX(stars['ALT'],stars['AZ'],stars.radio)
        s4=self.hallar_coordenadasY(stars['ALT'],stars['AZ'],stars.radio)
        stars2=pd.DataFrame({'X1':s1,'Y1':s2,'X2':s3,'Y2':s4})
        stars2.X1=self.anchura-stars2.X1
        stars2.Y1=self.altura-stars2.Y1
        stars2.X2=self.anchura-stars2.X2
        stars2.Y2=self.altura-stars2.Y2
        
        #x,y=self.rotar_pos(x,y)
        #x1,y1=self.rotar_pos(x1,y1)
        for index,row in stars2.iterrows():
            self.dwg.add(self.dwg.circle(center=((row['X1']+row['X2'])/2,(row['Y1']+row['Y2'])/2), r=(row['X1']-row['X2'])/6,fill='white'))#x-x1


    def start_drawing(self):
        self.dwg
        self.dwg.viewbox(0,0,self.anchura,self.altura)
        self.dwg.add(self.dwg.rect(insert=(0, 0), size=(self.anchura, self.altura),fill='white')) ####RECTANGULO - FONDO
        self.dwg.add(self.dwg.circle(center=(self.anchura/2,self.altura/2), r=self.anchura/2, fill=svgwrite.rgb(24, 24, 30))) #### CIRCULO - FONDO


  
    def calcular_pos_estrellas(self): #Obtiene un dataframe con las estrellas visibles
        
        self.db_estrellas['RA(rad)']=self.db_estrellas['RA(sex)'].apply(math.radians)
        self.db_estrellas['radio']=self.db_estrellas['MAG'].apply(self.calc_rad)
        self.db_estrellas['HA']=self.LMST_grados-self.db_estrellas['RA(rad)']
        
        self.db_estrellas["ALT"]=self.get_ALT(self.db_estrellas['DEC(rad)'],float(self.latitud),self.db_estrellas['HA'])
        self.db_estrellas["AZ"]=self.get_AZ(self.db_estrellas['DEC(rad)'],self.db_estrellas['ALT'],float(self.latitud),self.db_estrellas['HA'])
        
        visible_stars=self.db_estrellas[self.db_estrellas['ALT']>0]
        return visible_stars
        

################################# DIBUJAR - CONSTELACIONES ###############################
    def calcular_pos_const(self):
        
        #self.grafico = ImageDraw.Draw(self.imagen_principal)
        self.db_constelaciones['RA_INI']=self.db_constelaciones['RA_INI(sex)'].apply(math.radians)
        self.db_constelaciones['RA_FIN']=self.db_constelaciones['RA_FIN(sex)'].apply(math.radians)
        self.db_constelaciones['HA_INI']=self.LMST_grados-self.db_constelaciones['RA_INI']
        self.db_constelaciones['HA_FIN']=self.LMST_grados-self.db_constelaciones['RA_FIN']
        
        #Graficando constelaciones....
        self.db_constelaciones["ALT1"]=self.get_ALT(self.db_constelaciones['DEC_INI(rad)'],float(self.latitud),self.db_constelaciones['HA_INI'])
        self.db_constelaciones["AZ1"]=self.get_AZ(self.db_constelaciones['DEC_INI(rad)'],self.db_constelaciones['ALT1'],float(self.latitud),self.db_constelaciones['HA_INI'])
        self.db_constelaciones["ALT2"]=self.get_ALT(self.db_constelaciones['DEC_FIN(rad)'],float(self.latitud),self.db_constelaciones['HA_FIN'])
        self.db_constelaciones["AZ2"]=self.get_AZ(self.db_constelaciones['DEC_FIN(rad)'],self.db_constelaciones['ALT2'],float(self.latitud),self.db_constelaciones['HA_FIN'])
        visible_cons=self.db_constelaciones[(self.db_constelaciones['ALT1']>-0.05) & (self.db_constelaciones['ALT2']>-0.05)]
        
        return visible_cons
    
    def draw_const(self,cons):
        c1=self.hallar_coordenadasX(cons['ALT1'],cons['AZ1'])
        c2=self.hallar_coordenadasY(cons['ALT1'],cons['AZ1'])
        c3=self.hallar_coordenadasX(cons['ALT2'],cons['AZ2'])
        c4=self.hallar_coordenadasY(cons['ALT2'],cons['AZ2'])
        cons2=pd.DataFrame({'X1':c1,'Y1':c2,'X2':c3,'Y2':c4})
        cons2.X1=self.anchura-cons2.X1
        cons2.Y1=self.altura-cons2.Y1
        cons2.X2=self.anchura-cons2.X2
        cons2.Y2=self.altura-cons2.Y2
        for index,row in cons2.iterrows():
            #x,y=self.rotar_pos(x,y)
            #x1,y1=self.rotar_pos(x1,y1)
            self.dwg.add(self.dwg.line((row['X2'],row['Y2']),(row['X1'],row['Y1']), stroke='white',stroke_width = '0.2'))

################################ NOMBRES DE CONSTELACIONES ##########################
    def calcular_pos_names(self):     
        self.db_nombres_const['RA']=self.db_nombres_const['RA(sex)'].apply(math.radians)
        self.db_nombres_const['HA']=self.LMST_grados-self.db_nombres_const['RA']
        self.db_nombres_const['ALT']=self.get_ALT(self.db_nombres_const['DEC(rad)'],float(self.latitud),self.db_nombres_const['HA'])
        self.db_nombres_const['AZ']=self.get_AZ(self.db_nombres_const['DEC(rad)'],self.db_nombres_const['ALT'],float(self.latitud),self.db_nombres_const['HA'])
        visible_names=self.db_nombres_const[(self.db_nombres_const['ALT']>0.05) & (self.db_nombres_const['AZ']>0.05)]
        return visible_names
    
    
    def draw_names(self,names):
        names2=names.copy()
        names2['X']=self.hallar_coordenadasX(names['ALT'],names['AZ'])
        names2['Y']=self.hallar_coordenadasY(names['ALT'],names['AZ'])
        names2.X=self.anchura-names2.X
        
        names2.Y=self.altura-names2.Y
        for index,row in names2.iterrows():
        #if (math.sqrt(pow(abs(self.anchura/2-x),2)+pow(abs(self.altura/2-y),2))<=self.altura/2):
            nombre=row['NOMBRE']
            #x,y=self.rotar_pos(x, y)
            self.dwg.add(self.dwg.text(nombre, insert=(row['X'], row['Y']), fill='white', font_size=8,font_family="Calibri",font_style="oblique"))
                ##### LOS PARAMETROS DE GRAFICO.TEXT ERAN( X,Y )  AHORA PARA LA ROTACION ES (ANCHURA-X, ALTURA -Y)
    
################################### PARA PLANETAS ###################################
    def plotear_planetas(self):
        planetas = load('de421.bsp') #Cargando planetas
        
        self.earth, venus, sun, mercury,neptune,mars,saturn,jupyter,uranus,moon = planetas['earth'], planetas['venus'], planetas['sun'],planetas[1], planetas[8], planetas['mars'], planetas[6], planetas[5], planetas[7], planetas['moon']
        ts = load.timescale()
        t = ts.utc(self.fecha_hora.replace(tzinfo=utc))
        
        self.graficar_planeta(venus,t,'Venus')
        self.graficar_planeta(mercury,t,'Mercurio')
        self.graficar_planeta(mars,t,'Marte')
        self.graficar_planeta(saturn,t,'Saturno')
        self.graficar_planeta(jupyter,t,'Jupiter')
        self.graficar_planeta(neptune,t,'Neptuno')
        self.graficar_planeta(sun,t,'Sol')
        self.graficar_planeta(moon,t,'Luna')
        self.graficar_planeta(uranus,t,'Urano')
        
############################## DIBUJAR PLANETAS ##########################################
    def graficar_planeta(self,plnt,t,nombre):
        #long=len(nombre)
        position = self.earth.at(t).observe(plnt)
        ra, dec, distancia = position.radec()
        ra=ra.radians
        dec=dec.radians
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
    
    def guardar_imagen(self,nombre):
        self.dwg.filename='proyecto/static/images/'+nombre+'.svg'
        self.dwg.save()
        #self.imagen_principal.save('blog/media/'+nombre+'.jpg') ######### VACIO NO SE USA
        #print (time() - tiempo_inicial)


#FUNCION QUE ACOPLA OTRAS Y CREA PLOTEO DE ESTRELLAS CONSTELACIONES Y PLANETAS  
def funcion_principal(latitud,longitud,fecha_hora):
    astro=Astros(latitud,longitud,fecha_hora)
    astro.get_LMST(float(latitud),float(longitud))
    astro.read_databases()
    astro.start_drawing()
    stars=astro.calcular_pos_estrellas()
    astro.draw_stars(stars)
    cons=astro.calcular_pos_const()
    astro.draw_const(cons)
    nombres=astro.calcular_pos_names()
    astro.draw_names(nombres)
    astro.plotear_planetas()
    #astro.plotear_constelaciones()
    #astro.plotear_planetas()
    astro.guardar_imagen("astros"+latitud+"_"+fecha_hora.strftime("%Y-%m-%d-%H-%M-%S"))
    return stars



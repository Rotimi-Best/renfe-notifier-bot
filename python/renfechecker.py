#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
import pandas as pd
import optparse
import sys

class RenfeChecker:
    def __init__(self):
        self.driver = webdriver.Firefox()
        #self.driver.maximize_window()
        self.driver.get("http://www.renfe.com")

    def close(self):
        self.driver.close()

    def check_trip(self,orig,dest,dat_go,dat_ret=None):
        self.driver.get("http://www.renfe.com")
        time.sleep(1)
        self._checkTrains(orig, dest, dat_go, dat_ret)
        if self._areTrainsAvailable():
            print("There are trains available")
            return True,self._getTrainsDF()
        else:
            print("No trains available")
            return False,None


    def _checkTrains(self,orig,dest,dat_go,dat_ret):
        self._fill_elem("IdDestino",dest)
        self._fill_elem("IdOrigen",orig)
        self._fill_elem("__fechaIdaVisual",dat_go)
        self._fill_elem("__fechaVueltaVisual",dat_ret)
        bt = self.driver.find_element_by_class_name("btn.btn_home")
        bt.click()

    def _getTrainsDF(self):
        #df = pd.DataFrame(columns = ["SALIDA","LLEGADA","TIPO","PRECIO","CLASE","TARIFA","DISPONIBLE"])
        trayectos = []
        trenes = self.driver.find_element_by_id("listaTrenesTBodyIda")
        rows = trenes.find_elements_by_xpath(".//tr[@class='trayectoRow']")
        rows = rows + trenes.find_elements_by_xpath(".//tr[@class='trayectoRow row_alt']")
        rows = rows + trenes.find_elements_by_xpath(".//tr[@class='trayectoRow last']")
        for r in rows:
            sal = r.find_element_by_xpath(".//td[@headers='colSalida']").text
            lle = r.find_element_by_xpath(".//td[@headers='colLlegada']").text
            salT = datetime.datetime.strptime(sal, '%H.%M').time()
            lleT = datetime.datetime.strptime(lle, '%H.%M').time()
            toSec = lambda x: x.hour*60*60+x.minute*60+x.second
            dur = toSec(lleT)-toSec(salT)
            tipo = r.find_element_by_xpath(".//td[@headers='colTren']").text
            disp = not "Completo" in r.text and not "disponible" in r.text
            precio=""
            clase=""
            tarifa=""
            if disp:
                precio = r.find_element_by_xpath(".//td[@headers='colPrecio']").text
                precio = float(precio.split()[0].replace(",","."))
                clase = r.find_element_by_xpath(".//td[@headers='colClase']").text
                tarifa = r.find_element_by_xpath(".//td[@headers='colTarifa']").text
            trayectos.append({"SALIDA":salT,"LLEGADA":lleT,"TIPO":tipo,"PRECIO":precio,"DURACION":float(dur)/3600,"CLASE":clase,"TARIFA":tarifa,"DISPONIBLE":disp})
            # print("\n")
            # print(trayectos)
        df = pd.DataFrame(trayectos)
        df = df[["DISPONIBLE","SALIDA","LLEGADA","PRECIO","TIPO","DURACION","CLASE","TARIFA"]]
        df = df.sort_index(by="SALIDA")
        return df

    def _fill_elem(self,elem,data):
        if data == None:
            print("Not filling "+elem)
        else:
            print("Filling "+elem+" with "+data)
            el = self.driver.find_element_by_id(elem)
            el.clear()
            el.send_keys(data)
            time.sleep(0.5)
            el.send_keys(Keys.ENTER)


    def _areTrainsAvailable(self):
        nodata = self.driver.find_element_by_id("tab-mensaje_contenido")
        if "no se encuentra disponible" in nodata.text:
            return False
        else:
            return True;


def parse_arguments(argv):
  parser = optparse.OptionParser();
  parser.add_option("--origen","-o",help="Origen",default = None,dest ="origen")
  parser.add_option("--destino","-d",help="Destino",default = None,dest ="destino")
  parser.add_option("--fecha","-f",help="Fecha viaje",default = None,dest="fecha")
  options,args = parser.parse_args(argv);
  if options.origen is None or options.destino is None or options.fecha is None:
    print("Bad parameters");
    parser.print_help();
    exit(1);
  return options;


def printRes(aux,ori,des,fec):
    print("Results for=> origin: "+ori+", dest: "+des+", date: "+fec)
    if aux[0]:
        print(aux[1])
    else:
        print("NO RESULTS")

def main(ori,des,fec):
    rf = RenfeChecker()
    aux = rf.check_trip(ori,des,fec)
    printRes(aux, ori, des, fec)
    aux = rf.check_trip(des,ori,fec)
    printRes(aux, des, ori, fec)
    rf.close()


if __name__ == "__main__":
    op = parse_arguments(sys.argv)
    main(op.origen,op.destino,op.fecha)
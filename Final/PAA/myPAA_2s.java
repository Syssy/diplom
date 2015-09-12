import mosdi.paa.DeterministicEmitter;
import mosdi.paa.PAA;
import java.util.Date;
import java.io.*;

public class myPAA_2s extends PAA implements DeterministicEmitter{

	/**
	 * @param args
	 * Zustand 0 ist stationaer, Zustand 1 mobil
	 * Zum Starten:  javac -classpath mosdi-1.3.jar myPAA_2s.java und dann:
         *               java -classpath .:mosdi-1.3.jar myPAA_2s
         * (mosdi muss im gleichen Verzeichnis liegen)
	 */
	 
	// maximale Wartezeit; wie sonst auch 2400000 (240s * 10000 Schritte/s)
	static int MAXTIME = 2400000;
	// Laenge der Saeule
	static int LENGTH = 1000;
        static double[] params = new double[2];
	
	public static void main(String[] args) {
                // Parameterkombi waehlen
                double[][] param_list = combineParams();
                double[] arrivals = new double[0];
                // alle gewaehlten Kombis simulieren
                for (int i = 0; i < param_list.length; i++){
                    params = param_list[i];
                    String csvfile = "savedata_java/2s/l" + LENGTH + "/Sim_" + params[0] + "_"+ params[1];
                    System.out.println(csvfile);
                    PAA aPAA = new myPAA_2s();
                    // Zeiten nur aus Interesse
                    for (int j = 0; j < 5; j++){
                    long starttime = System.currentTimeMillis();
                    // mosdi starten
                    arrivals = aPAA.waitingTimeForValue(MAXTIME, LENGTH);
                    long endtime = System.currentTimeMillis();
                    System.out.println("Time: " + (endtime - starttime)/1000 + " seconds");
                    }
                    
                    // Zur Kontrolle, ob Peak vollständig: Summe berechnen
                    double sum = 0.0;
                    for( double arr : arrivals) {
                        sum = sum+arr;
                    } 
                    System.out.println("Sum " + sum);
                    // Ergebnisse speichern
                    try{
                        FileWriter writer = new FileWriter(csvfile);
                        for (double z : arrivals){
                            writer.write(Double.toString(z));
                            writer.write("\n");
                            }
                        writer.close();
                    } catch (IOException ex){
                        ex.printStackTrace();
                        }
                } 
		System.out.println("Done");
	}
	
	
        public static double[][] combineParams(){
            // gewuenschte Parametereinstellungen
            double[] ps_list = new double[] {0.997, 0.999, 0.9993, 0.9996};//, 0.9999};
            double[] pm_list = new double[] {0.001, 0.3, 0.6, 0.95};
            double[][] param_list = new double[16][2];
            
            for (int i = 0; i<ps_list.length; i++){
                for (int j = 0; j<pm_list.length; j++){
             //       System.out.println(i + " " + j + " " + (i*4+ j));
                    param_list[i*4 + j] = new double[]{ps_list[i], pm_list[j]};
                }
            }
            
        return param_list;
        }

	@Override
	public double emissionProbability(int state, int emission) {
	// Zustand 1 hat immer Emission 1 und Z0 hat E0, daher dort 1, sonst 0
		if (state == emission){
			return 1;
		} else {
			return 0;
		}
	}

	@Override
	public int getEmissionCount() {
	// Emissionen 0 und 1 moeglich
		return 2;
	}

	@Override
	public int getStartState() {
	// Beginne mobil = 1
		return 1;
	}

	@Override
	public int getStartValue() {
	// Beginne an Ort 0
		return 0;
	}

	@Override
	public int getStateCount() {
	// Zustaende 0 und 1
		return 2;
	}

	@Override
	public int getValueCount() {
	//Entspricht der maximalen Wartezeit, da alle ganzzahligen Werte bis dahin erreicht werden können
	// plus zwei, da sonst bei Eintreffen am Ende Fehler auftreten
		return LENGTH + 2;
	}

	@Override
	public int performOperation(int state, int value, int emission) {
	// Operation ist immer "+", ausser nach erreichen der maximalen Schritte
		if (value + emission < getValueCount() - 1){
			return value + emission;
		} else {
			return value;
		}
	}

	@Override
	public double transitionProbability(int state, int targetState) {
	// Wahrscheinlichkeiten anhand der params ausgeben
                switch(state){
                case 0: 
                    switch(targetState){
                        case 0: return params[0];
                        case 1: return 1 - params[0];
                        default: return 0.0;
                        }
                case 1:
                    switch(targetState){
                        case 0: return 1 - params[1];
                        case 1: return params[1];
                        default: return 0.0;
                        }
                default: return 0.0;
                }
	}

	@Override
	public int getEmission(int state) {
	// Bei Zustand 1 (=mobil) gehe 1 sonst nicht
		if (state == 1){
			return 1;
		} else {
			return 0;	
		}
	}

}

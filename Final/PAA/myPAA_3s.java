import mosdi.paa.DeterministicEmitter;
import mosdi.paa.PAA;
import java.util.Date;
import java.io.*;

public class myPAA_3s extends PAA implements DeterministicEmitter{

	/**
	 * @param args
	 * 3 Zustaende, 0 entspricht mobil, 1 und 2 die stationaeren
	 * Zum Starten:  javac -classpath mosdi-1.3.jar myPAA_3s.java und dann:
         *               java -classpath .:mosdi-1.3.jar myPAA_3s
         * (mosdi muss im gleichen Verzeichnis liegen)
	 */
	
	// Maximale Wartezeit und Laenge
	static int MAXTIME = 2400000;
	static int LENGTH = 1000;
	static double[] params = new double[9];
	
	public static void main(String[] args) {
                // Parameter kombinieren
                double[][] parameterliste = combineParams();
                double [] arrivals = new double[1];
                // alle Parameterkombinationen simulieren
                for (int i = 0; i < parameterliste.length; i++){
                    params = parameterliste[i];
                    PAA aPAA = new myPAA_3s();
                    // Zeit nur aus Interesse
                    long starttime = System.currentTimeMillis();
                    // mosdi starten
                    arrivals = aPAA.waitingTimeForValue(MAXTIME, LENGTH);
                    long endtime = System.currentTimeMillis();
                    System.out.println("Time: " + (endtime - starttime)/1000 + " seconds");
                    double sum = 0.0;
                    for( double num : arrivals) {
                        sum = sum+num;
                    }
                    System.out.println("Sum " + sum);
                    // Ergebnis speichern
                    String csvfile = "savedata_java/l" + LENGTH + "/3_states/Sim_" + params[0] + "_"+ params[1] + "_"+ params[2] + "_"+ params[3] + "_"+ params[4] + "_"+ params[5] + "_" + params[6] + "_" + params[7] + "_" + params[8];
                    System.out.println(csvfile);
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
            // Parametereinstellungen
            double[][] param_list = new double[15][9];
            param_list[0] = new double[] {0.7, 0.29995, 0.00005, 0.005, 0.995, 0.0, 0.0001, 0.0, 0.9999};
            param_list[0] = new double[] {0.3, 0.7, 0.0, 0.003, 0.997, 0.0, 0.0001, 0.0, 0.9999};        
            param_list[1] = new double[] {0.99, 0.005, 0.005, 0.0004, 0.9996, 0.0, 0.000025, 0.0, 0.999975};
            param_list[2] = new double[] {0.99, 0.0095, 0.0005, 0.005, 0.995, 0.0, 0.000075, 0.0, 0.999925};
            param_list[3] = new double[] {0.85, 0.1493, 0.0007, 0.003, 0.997, 0.0, 0.000003, 0.0, 0.999997};
            param_list[4] = new double[] {0.005, 0.99499, 0.00001, 0.0009, 0.9991, 0.0, 0.0001, 0.0, 0.9999};
            param_list[5] = new double[] {0.6, 0.399, 0.001, 0.0004, 0.9996, 0.0, 0.0001, 0.0, 0.9999};
            param_list[6] = new double[] {0.005, 0.9947, 0.0003, 0.0009, 0.9991, 0.0, 0.000003, 0.0, 0.999997};
            param_list[7] = new double[] {0.5, 0.499, 0.001, 0.0005, 0.9995, 0.0, 0.00001, 0.0, 0.99999};
            param_list[8] = new double[] {0.05, 0.9495, 0.0005, 0.0009, 0.9991, 0.0, 0.000005, 0.0, 0.99995};
            param_list[9] = new double[] {0.2, 0.7993, 0.0007, 0.0008, 0.9992, 0.0, 0.000004, 0.0, 0.999996};
            param_list[10] = new double[] {0.005, 0.999499, 0.00001, 0.0005, 0.9995, 0.0, 0.0001, 0.0, 0.9999};
            param_list[11] = new double[] {0.15, 0.84995, 0.00005, 0.0004, 0.9996, 0.0, 0.0001, 0.0, 0.9999};
            param_list[12] = new double[] {0.05, 0.9493, 0.0007, 0.0005, 0.9995, 0.0, 0.000025, 0.0, 0.999975};
            param_list[13] = new double[] {0.15, 0.845, 0.005, 0.0005, 0.9995, 0.0, 0.000025, 0.0, 0.999975};
            param_list[14] = new double[] {0.1, 0.899, 0.001, 0.0007, 0.9993, 0.0, 0.000001, 0.0, 0.999999};
          
        return param_list;
	}
	
	@Override
	public double emissionProbability(int state, int emission) {
                // Zustand 0 emittiert immer 1, die anderen immer 0
		if ( (state == 0 && emission == 1)  ||  ((state == 1 || state == 2) && emission == 0) ){
			return 1;
		} else {
			return 0;
		}
	}

	@Override
	public int getEmissionCount() {
	// Emissionen 0 und 1 zulaessig
		return 2;
	}

	@Override
	public int getStartState() {
	// Starte mobil = 0
		return 0;
	}

	@Override
	public int getStartValue() {
	// Starte bei Ort 0
		return 0;
	}

	@Override
	public int getStateCount() {
	// 3 Zustaende: Mobil, stationaer 1 & 2
		return 3;
	}

	@Override
	public int getValueCount() {
        // maxtime plus puffer gegen fehler
	//	return MAXTIME + 2;
                return LENGTH + 2;
	}

	@Override
	public int performOperation(int state, int value, int emission) {
	// Immer "+" ausser nach erreichen der maximal erlaubten schritte
		if (value + emission < getValueCount() - 1){
			return value + emission;
		} else {
			return value;
		}
	}

	@Override
	public double transitionProbability(int state, int targetState) {
	// Hier werden die Wkeiten aus den params gezogen
                switch(state){
                case 0: // 
                    switch(targetState){
                        case 0: return params[0];
                        case 1: return 1 - params[0] - params[2];
                        case 2: return params[2];
                        default: return 0.0;
                        }
                case 1:
                    switch(targetState){
                        case 0: return 1 - params[4];
                        case 1: return params[4];
                        case 2: return 0.0;
                        default: return 0.0;
                        }
                case 2:
                    switch(targetState){
                        case 0: return 1 - params[8];
                        case 1: return 0.0;
                        case 2: return params[8];
                        default: return 0.0;
                        }
                default: return 0.0;
                } 
	}

	@Override
	public int getEmission(int state) {
	// Emission 1 in Zustand 0, sonst 0
		if (state == 0){
			return 1;
		} else {
			return 0;	
		}
	}

}

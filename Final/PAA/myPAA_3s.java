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
                    String csvfile = "savedata_java/3a/l" + LENGTH + "/Sim_" + params[0] + "_"+ params[1] + "_"+ params[2] + "_"+ params[3] + "_"+ params[4] + "_"+ params[5] + "_" + params[6] + "_" + params[7] + "_" + params[8];
                    System.out.println(csvfile);
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
            // Parametereinstellungen fuer Modell 3a
            double[] pmm_list = new double[] {0.1, 0.5, 0.9};
            double[] pml_list = new double[] {0.001, 0.0005, 0.0001};
            double[] paa_list = new double[] {0.999, 0.9993, 0.9996};
            double[] pll_list = new double[] {0.99995, 0.99999, 0.999995};
            double[][] param_list = new double[81][2];
            
            for (int i = 0; i<pmm_list.length; i++){
                for (int j = 0; j<pml_list.length; j++){
                    for (int k = 0; k<paa_list.length; k++){
                        for (int l = 0; l<pll_list.length; l++){
                    //       System.out.println(i + " " + j + " " + (i*4+ j));
                            param_list[i*8 + j*4 +k*2 +l] = new double[]{pmm_list[i], (1-pmm_list[i]-pml_list[j]), pml_list[j], (1-paa_list[k]), paa_list[k], 0.0, (1-pll_list[l]), 0.0, pll_list[l]};
                        }    
                    }
               }
            }
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

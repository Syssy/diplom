import mosdi.paa.DeterministicEmitter;
import mosdi.paa.PAA;
import java.util.Date;
import java.io.*;

public class myPAA_2p extends PAA implements DeterministicEmitter{

	/**
	 * @param args
	 * Zustand 0 ist stationaer, Zustand 1 mobil
	 * Zum Starten:  javac -classpath mosdi-1.3.jar myPAA_2p.java und dann:
         *               java -classpath .:mosdi-1.3.jar myPAA_2p
         * (mosdi muss im gleichen Verzeichnis liegen)
	 */
	 
	// maximale Wartezeit; wie sonst auch 2400000 (240s * 10000 Schritte/s)
	static int MAXTIME = 2400000;
	static int LENGTH = 999;
        static double[] params = new double[2];
	
	public static void main(String[] args) {
		
                double[][] parameterliste = combineParams();
                double[] x = new double[0];
                for (int i = 0; i < parameterliste.length; i++){
                    params = parameterliste[i];
                    PAA aPAA = new myPAA_2p();
                    //System.out.println(params[0]);
                    Date startdate2 = new Date();
                    String csv = "savedata_java/l999/2p/Sim_" + params[0] + "_"+ params[1];
                    //csv = "dingsda3s";
                    System.out.println(csv);
                    double sum = 0.0;
                    int schleifen[] = {1,2,3,4,5};
                    for (int z : schleifen){
                        long starttime = System.currentTimeMillis();
                        // maxtime, value !!!
                        x = aPAA.waitingTimeForValue(MAXTIME, LENGTH);
                        long endtime = System.currentTimeMillis();
                        System.out.println("Zeit: " + (endtime - starttime));
                        for( double num : x) {
                            sum = sum+num;
                        }
                    } 
                    //ausgabe1(x);
                    System.out.println("Summe " + sum);
                    Date enddate2 = new Date();
                // Ergebnisse speichern. TODO Flexibler machen
		try{
                    FileWriter writer = new FileWriter(csv);
                    for (double z : x){
                        writer.write(Double.toString(z));
                        writer.write("\n");
                        }
                    writer.close();
                } catch (IOException ex){
                ex.printStackTrace();
                }
                }   
                Date enddate2 = new Date();
              //  System.out.println(startdate2 + " "+ enddate2);
		System.out.println("Fertig");
	}
	
	
        public static double[][] combineParams(){
        
            double[] ps_list = new double[] {0.997, 0.999, 0.9992, 0.9995, 0.9999};
            double[] pm_list = new double[] {0.01, 0.3, 0.9, 0.99};
            double[][] param_list = new double[20][2];
            
            for (int i = 0; i<ps_list.length; i++){
                for (int j = 0; j<pm_list.length; j++){
             //       System.out.println(i + " " + j + " " + (i*4+ j));
                    param_list[i*4 + j] = new double[]{ps_list[i], pm_list[j]};
                }
            }
            //ausgabe2(param_list);
            
        return param_list;
        }

	public static void ausgabe1(double[] anArray){
	// Ausgabe eines double[]
		for (int i = 0; i < anArray.length; i++){
			System.out.print(anArray[i]+" ");
		}
	}

	public static void ausgabe2(double[][] anArray){
	// Ausgabe eines double[][]
		for (int i = 0; i < anArray.length; i++){
			for (int j = 0; j < anArray[i].length; j++){
				System.out.print(anArray[i][j] + " ");
			}
			System.out.println(" ");
		}
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
	// Hier werden die Wahrscheinlichkeiten eingestellt
// 		double ps = 0.9;
// 		double pm = 0.9995;
// 		double p;
// 		switch (state){
// 		case 0: p = ps; break;
// 		case 1: p = pm; break;
// 		default: p = 0; break;	
// 		}
// 		if (state == targetState){
// 			return p;
// 		} else {
// 			return 1-p;
// 		}
                switch(state){
                case 0: // [0.6f0 0.399f0 0.001f0; 0.0004f0 0.9996f0 0.0f0; 0.0001f0 0.0f0 0.9999f0]
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

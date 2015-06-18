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
	 
	static int MAXTIME = 24000
	
	public static void main(String[] args) {
		PAA aPAA = new myPAA_3s();

		Date startdate2 = new Date();
		// maxtime, value !!!
		double[] x = aPAA.waitingTimeForValue(MAXTIME, 100);
		double sum = 0.0;
                for( double num : x) {
                    sum = sum+num;
                } 
 		ausgabe1(x);
                System.out.println("Summe " + sum);
                // Ergebnis speichern
		try{
                    String csv = "output3";
                    FileWriter writer = new FileWriter(csv);
                    for (double z : x){
                        writer.write(Double.toString(z));
                        writer.write("\n");
                        }
                    writer.close();
                } catch (IOException ex){
                ex.printStackTrace();
                }
		Date enddate2 = new Date();
		System.out.println(startdate2 + " "+ enddate2);

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
		return MAXTIME + 2;
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
	// Hier koennen die Wahrscheinlichkeiten eingestellt werden
                switch(state){
                case 0:
                    switch(targetState){
                        case 0: return 0.3;
                        case 1: return 0.69;
                        case 2: return 0.01;
                        default: return 0.0;
                        }
                case 1:
                    switch(targetState){
                        case 0: return 0.001;
                        case 1: return 0.999;
                        case 2: return 0.0;
                        default: return 0.0;
                        }
                case 2:
                    switch(targetState){
                        case 0: return 0.00005;
                        case 1: return 0.0;
                        case 2: return 0.99995;
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

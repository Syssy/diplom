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
	public static void main(String[] args) {
		PAA aPAA = new myPAA_2p();
		//System.out.println(aPAA.stateValueStartDistribution());
		//ausgabe2(aPAA.stateValueStartDistribution());
		
//		//Teste, was für mich schneller ist, wegen der doublingtechnique
// 		Date startdate1 = new Date();
// 		//double[][] ausgabe = aPAA.computeStateValueDistribution(100000);
// 		Date enddate1 = new Date();
// 		System.out.println(startdate1 + " " + enddate1);

		Date startdate2 = new Date();
		// maxtime, value !!!
		double[] x = aPAA.waitingTimeForValue(30000, 1000);
		double sum = 0.0;
                for( double num : x) {
                    sum = sum+num;
                } 
 		//ausgabe1(x);
                System.out.println("Summe " + sum);
		try{
                    String csv = "savedata_java/l1000/0.999_0.999.csv";
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
		for (int i = 0; i < anArray.length; i++){
			System.out.print(anArray[i]+" ");
		}
	}

	public static void ausgabe2(double[][] anArray){
		for (int i = 0; i < anArray.length; i++){
			for (int j = 0; j < anArray[i].length; j++){
				System.out.print(anArray[i][j] + " ");
			}
			System.out.println(" ");
		}
	}
	
	@Override
	public double emissionProbability(int state, int emission) {
		if (state == emission){
			return 1;
		} else {
			return 0;
		}
	}

	@Override
	public int getEmissionCount() {
		return 2;
	}

	@Override
	public int getStartState() {
		return 1;
	}

	@Override
	public int getStartValue() {
		return 0;
	}

	@Override
	public int getStateCount() {
		return 2;
	}

	@Override
	public int getValueCount() {
		return 30002;
	}

	@Override
	public int performOperation(int state, int value, int emission) {
		if (value + emission < getValueCount() - 1){
			return value + emission;
		} else {
			return value;
		}
	}

	@Override
	public double transitionProbability(int state, int targetState) {
		double ps = 0.999;
		double pm = 0.999;
		double p;
		switch (state){
		case 0: p = ps; break;
		case 1: p = pm; break;
		default: p = 0; break;	
		}
		if (state == targetState){
			return p;
		} else {
			return 1-p;
		}


	}

	@Override
	public int getEmission(int state) {
		if (state == 1){
			return 1;
		} else {
			return 0;	
		}
	}

}

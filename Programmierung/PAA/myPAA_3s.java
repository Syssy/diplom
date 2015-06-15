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
	public static void main(String[] args) {
		PAA aPAA = new myPAA_3s();
		//System.out.println(aPAA.stateValueStartDistribution());
		//ausgabe2(aPAA.stateValueStartDistribution());
		
//		//Teste, was für mich schneller ist, wegen der doublingtechnique
// 		Date startdate1 = new Date();
// 		//double[][] ausgabe = aPAA.computeStateValueDistribution(100000);
// 		Date enddate1 = new Date();
// 		System.out.println(startdate1 + " " + enddate1);

		Date startdate2 = new Date();
		// maxtime, value !!!
		double[] x = aPAA.waitingTimeForValue(30000, 100);
		double sum = 0.0;
                for( double num : x) {
                    sum = sum+num;
                } 
 		ausgabe1(x);
                System.out.println("Summe " + sum);
		try{
                    String csv = "output2";
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
                // 
		if ( (state == 0 && emission == 1)  ||  ((state == 1 || state == 2) && emission == 0) ){
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
		return 0;
	}

	@Override
	public int getStartValue() {
		return 0;
	}

	@Override
	public int getStateCount() {
		return 3;
	}

	@Override
	public int getValueCount() {
		// TODO Auto-generated method stub
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
// 		double ps = 0.9992;
// 		double pm = 0.99;
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
                case 0:
                    switch(targetState){
                        case 0: return 0.4;
                        case 1: return 0.599;
                        case 2: return 0.001;
                        default: return 0.0;
                        }
                case 1:
                    switch(targetState){
                        case 0: return 0.01;
                        case 1: return 0.99;
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
		if (state == 0){
			return 1;
		} else {
			return 0;	
		}
	}

}

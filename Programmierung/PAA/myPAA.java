import mosdi.paa.DeterministicEmitter;
import mosdi.paa.PAA;
import java.util.Date;

public class myPAA extends PAA implements DeterministicEmitter{

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		PAA aPAA = new myPAA();
		//System.out.println(aPAA.stateValueStartDistribution());
		//ausgabe2(aPAA.stateValueStartDistribution());
		
		//Teste, was für mich schneller ist, wegen der doublingtechnique
		Date startdate1 = new Date();
		double[][] ausgabe = aPAA.computeStateValueDistribution(50000);
		Date enddate1 = new Date();
		System.out.println(startdate1 + " "+ enddate1);

		Date startdate2 = new Date();
		aPAA.waitingTimeForValue(50000, 10000);
		Date enddate2 = new Date();
		System.out.println(startdate2 + " "+ enddate2);
		
		// TODO Auto-generated method stub

	}

	public static void ausgabe1(double[] anArray){
		for (int i = 0; i < anArray.length; i++){
			System.out.print(anArray[i]);
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
		// TODO Auto-generated method stub
		return 50000;
	}

	@Override
	public int performOperation(int state, int value, int emission) {
		if (value + emission < getValueCount() -1){
			return value + emission;
		} else {
			return value;
		}
	}

	@Override
	public double transitionProbability(int state, int targetState) {
		double ps = 0.99;
		double pm = 0.99;
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
		if (state == 0){
			return 0;
		} else {
			return 1;	
		}
	}

}

package org.usfirst.frc.team166.robot.commands.drive;

import edu.wpi.first.wpilibj.command.Command;

import org.usfirst.frc.team166.robot.Robot;

/**
 *
 */
public class TurnToGoalParallel extends Command {

	public TurnToGoalParallel() {
		// Use requires() here to declare subsystem dependencies
		requires(Robot.drive);
	}

	// Called just before this Command runs the first time
	@Override
	protected void initialize() {
		Robot.drive.resetGyro();
	}

	// Called repeatedly when this Command is scheduled to run
	@Override
	protected void execute() {
		// Robot.drive.turn(-2 * Robot.vision.getXOffset(), 2 * Robot.vision.getXOffset());
		if (Math.abs(Robot.vision.getXOffset()) > .05) {
			Robot.drive.turnToGoalParallel(Robot.vision.getXOffset());
		} else {
			Robot.drive.stop();
		}
	}

	// Make this return true when this Command no longer needs to run execute()
	@Override
	protected boolean isFinished() {
		// return (Math.abs(Robot.vision.getXOffset()) < .05);
		return false;
	}

	// Called once after isFinished returns true
	@Override
	protected void end() {
		Robot.drive.turnToGoalAngle = Robot.drive.getGyro();
	}

	// Called when another command which requires one or more of the same
	// subsystems is scheduled to run
	@Override
	protected void interrupted() {
	}
}

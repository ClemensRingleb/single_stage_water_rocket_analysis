README ----------------- water-rocket

 .---------------------------.
(   ███████╗ ██████╗ ██████╗  )
(   ██╔════╝██╔════╝██╔══██╗  )
(   █████╗  ██║  ███╗██║  ██║ )
(   ██╔══╝  ██║   ██║██║  ██║ )
(   ███████╗╚██████╔╝██████╔╝ )
(   ╚══════╝ ╚═════╝ ╚═════╝  )
 '---------------------------'

__        ___    _____ _____ _____      _____   ____   ____ _  ________ _______          /\
\ \      / / \  |_   _| ____|  __ \    |  __ \ / __ \ / ___| |/ / ____|__   __|         /  \
 \ \ /\ / / _ \   | | |  _| | |__) |   | |__) | |  | | |   | ' /|  _|    | |           /++++\
  \ V  V / ___ \  | | | |___|  _  /    |  _  /| |__| | |___| . \| |___   | |          /      \
   \_/\_/_/   \_\ |_| |_____|_| \_\    |_| \_\ \____/ \____|_|\_\_____|  |_|          |      |
                                                                                      |      |
                                                                                     /|______|\
                                                                                    /_/______\_\
                                                                                      /_/  \_\
                                                                                         ||
                                                                                         ||
                                                                                       ~~~~~~
                                                                                     ~~~~~~~~~~
                                                                                   ~~~~~~~~~~~~~~
                                                                                 ~~~~~~~~~~~~~~~~~

------------- Deutsch/german ----------------

Dieses Projekt wurde im Rahmen einer Facharbeit im Rahmen des Unterrichts in der 12.Klasse von Clemens Ringleb erstellt. 
Alle Rechte vorbehalten. Die Vervielfältigung ist, sofern nicht anders angegeben, untersagt und unterliegt in jedem Fall
der Freigabe durch den Autor.

Im Ordner findet man die .stl Datei zu den von mir verwendeten Finnen der Rakete. Ggf. sollten diese noch nach unten hin verlängert
werden um mehr Stabilität zu gewährleiten.

Die eigentliche Simulation liegt in einem einfachen Python code "simulation_water_rocket_monoplot" (Durchführung und Plot eines einzelnen Fluges)
bzw. "simulation_water_rocket_multiple_plot" (gleiches für mehrere flüge in der selben Darstellungform) vor. 
Zur reibungslosen Durchführung sind die Pakete/Libraries "pygame", "numpy" und "matplotlib" essentiell.
Hierzu einfach installieren (unter Windows):

	py -m pip install pygame
	py -m pip install numpy
	py -m pip install matplotlib


Im Ordner "_massflow" liegen zunächst die Videos zur Überprüfung des Massenstroms durch die vorliegende Düse.
Videos zu meinen Starts, die als Grundlage meiner Höhenmessung dienen, findet man unter "flight_videos" bzw. "flight_videos_short".
Gesammelte Daten zu maximalen Höhen (und zugehörigen t_max) findet man unter "max_data_exp" (experimentelle Daten) und "max_data_sim" (Simulationsdaten).

Zur Analyse der videografisch festgehaltenen Höhen wurde das Programm "Tracker" genutzt.

Der Luftwiderstand wurde mit C_D = 0,4 für eine schmale zylindrische PET-Flasche (langer Zylinder, gute Aerodynamik) gewählt und ist je nach 
Umsetzung anzupassen.

Die tick-differenz der Simulation liegt bei dt = 10^(-5) kann aber nach Belieben erhöht oder verringert werden. Bei Verringerung ist mit 
Unsicherheiten, bei Erhöhung mit längeren Ladezeiten zu rechnen.

Viel Spaß bei der eigenen Weiterentwicklung!



------------- English ----------------

This project as well as all the related stuff was created by Clemens Ringleb as part of a "School project" in 12th grade.
All rights reserved. Publishing the work or any related stuff is, unless otherwise stated, prohibited. The approval of the author is required in 
any case of use.

You can find the .stl file of the rocket finns I used in the folder. You can try to make them longer to ensure better stabilty of the rocket
in the air.

The actual simulation is implemented in a simple Python code: "simulation_water_rocket_monoplot" (execution and plot of a single flight) and 
"simulation_water_rocket_multiple_plot" (the same, but for multiple flights shown in a single plot).

For smooth execution, the packages/libraries "pygame", "numpy", and "matplotlib" are essential.
To install them on Windows, simply run:

	py -m pip install pygame
	py -m pip install numpy
	py -m pip install matplotlib

The folder "_massflow" contains videos used to verify the mass flow through the nozzle.
Videos of my rocket launches, which serve as the basis for my altitude measurements, can be found under "flight_videos" and "flight_videos_short".

For the analysis of the video-recorded altitudes, the program "Tracker" was used.

The drag coefficient was set to C_D = 0.4, corresponding to a slender cylindrical PET bottle (long cylinder, good aerodynamics). It should be adjusted 
depending on your specific setup.

The simulation time step is dt = 10^(-5), but this can be increased or decreased as desired.
Decreasing it may lead to numerical uncertainties, while increasing it will result in longer loading times.

Enjoy further developing your own version!




README END ----------------------------------------

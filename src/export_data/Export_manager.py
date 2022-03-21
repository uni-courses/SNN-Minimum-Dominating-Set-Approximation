# Main code that performs computations for this project.


class Export_manager:
    """ """

    def __init__(self):
        # Path related variables
        self.relative_src_filepath = f"src/"

        # PlantUML related variables
        self.plant_uml_java_filename = "plantuml.jar"
        self.relative_plant_uml_java_filepath = f"src/{self.plant_uml_java_filename}"
        self.diagram_dir = "Diagrams"
        self.static_diagram_dir = "Static_diagrams"
        self.src_to_diagram_path = f"{self.relative_src_filepath}{self.diagram_dir}/"
        self.gantt_text_extension = ".uml"

        # Run main code.
        print(f"5+2={self.add_two(5)}")

    def add_two(self, x):
        """adds two to the incoming integer and returns the result of the computation.

        :param x: Integer number.

        """
        return x + 2

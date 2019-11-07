
import problemGenerator.Generator as Generator


if __name__ == "__main__":
    generator = Generator.Generator()
    generator.generateNodes()
    for node in generator.nodes:
        print(node.str())
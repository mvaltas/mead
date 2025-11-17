import matplotlib.pyplot as plt


class Graph:

    def plot(self, results):
        for k in results.keys():
            plt.plot(results[k], label=k)

        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.grid(True)
        plt.legend()
        plt.title("Simulation")
        plt.savefig("plot.png")

        plt.show()

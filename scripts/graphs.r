library(gridExtra)

data_1k = read.csv("../data/1k_results.txt")
data_100k = read.csv("../data/100k_1_results.txt")
data_100k_2 = read.csv("../data/100k_2_results.txt")

# Aggregate the bits per second and the window size
data_1k_ag = aggregate(bps~window, data_1k, mean)
data_100k_ag = aggregate(bps~window, data_100k, mean)

# Create the plots
png("100k_window.png", width=600, height=500)
plot(bps~window, data_100k_ag, main="BPS vs Window Size", xlab="Window Size", 
	ylab="Bits Per Second", col="red", pch=16)
dev.off()

# Aggregate the bits per second and the latency
data_100k_ag = aggregate(bps~latency, data_100k_2, mean)

# Create the plots
png("100k_lateny.png", width=600, height=500)
plot(bps~latency, data_100k_ag, main="BPS vs Latency", xlab="Latency ms", 
	ylab="Bits Per Second", col="green", pch=16)
dev.off()

# Aggregate the bits per second and the MSS
data_100k_ag = aggregate(bps~mss, data_100k, mean)

# Create the plots
png("100k_mss.png", width=600, height=500)
plot(bps~mss, data_100k_ag, main="BPS vs MSS", xlab="MSS bytes", 
	ylab="Bits Per Second", col="blue", pch=16)
dev.off()

# Aggregate the bits per second and the drop percentage
data_100k_ag = aggregate(bps~loss, data_100k_2, mean)

# Create the plots
png("100k_loss.png", width=600, height=500)
plot(bps~loss, data_100k_ag, main="BPS vs Drop %", xlab="Drop %", 
	ylab="Bits Per Second", col="purple", pch=16)
dev.off()
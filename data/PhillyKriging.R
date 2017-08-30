
library(geoR)
library(automap)
library(rgdal)
library(ggplot2)
philly_data <- read.table('/Users/smooney/streetview/data/philadelphia-final.csv', header=T, stringsAsFactors=F, sep=",")

# Proof of concept: Disorder Index where n'hood gets one point for each of: trash, empty bottles, graffiti, abandoned cars, abandoned buildings and burned out buildings.
philly_data$physical_disorder <- philly_data$PHDCN.1 + philly_data$PHDCN.2 + philly_data$PHDCN.3 + philly_data$PHDCN.4 + philly_data$PHDCN.6 + philly_data$PHDCN.7
philly_short <- philly_data[-which(duplicated(philly_data$Segment.ID)),]
philly_short <- philly_short[-which(is.na(philly_short$physical_disorder)),]

# Plot non-kriged data for comparison
plot(philly_short, col=philly_short$physical_disorder, pch=19)
legend("topleft", legend=1:max(philly_short$physical_disorder), col=1:max(philly_short$physical_disorder), pch=19)

#philly_short <- philly_data
coordinates(philly_short) <- c("start_lng", "start_lat")
proj4string(philly_short) <- CRS("+proj=longlat")
projected_philly = spTransform(philly_short, CRS("+proj=merc +zone=18s +ellps=WGS84 +datum=WGS84"))

# autoKrige experiment
kr <- autoKrige(physical_disorder~1, projected_philly)
plot(kr)

# Kriging using Mike's recommended function

# First, the variogram:
variogram <- variog(coords=coordinates(projected_philly), data=projected_philly$physical_disorder, max.dist=1)
loci <- matrix(c(-75.20, 40.00), nrow=1, ncol=2)
control <- krige.control(cov.pars=c(1,.25))
krige.conv(coords=coordinates(projected_philly), data=projected_philly$physical_disorder, loc=loci, krige=control)
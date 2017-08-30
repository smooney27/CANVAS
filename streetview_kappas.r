library(irr)
library(epiR)
all_150 <- read.table("~/Projects/stats/150_blocks.csv", header=T, sep=",")
raters <- c(4, 11, 14)
full_data <- all_150[which(all_150$User %in% raters),]
all_raters <- all_150[which(all_150$Segment < 129),]
full_150 <- full_data[which(full_data$Segment <= 257),]


# Kappas
construct_results_matrix <- function(dataset, column) {
    columns <- names(dataset)
    raters <- unique(dataset$User[!is.na(dataset$User)])
    segments <- unique(dataset$Segment[!is.na(dataset$Segment)])
    results_matrix <- matrix(ncol=length(segments), nrow=length(raters), dimnames=list(raters, segments))
    full_data_segments <- c()
    for (segment in segments) {
        missing_data = FALSE;
        for (rater in raters) {
            if (0 == nrow(dataset[which(dataset$User == rater & dataset$Segment == segment),])) {
                missing_data = TRUE;
                break;
            }
        }
        if (missing_data == TRUE) {
            next;
        }
        full_data_segments <- c(full_data_segments, as.character(segment))
        for (rater in raters) {
            rated_segment <- dataset[which(dataset$User == rater & dataset$Segment == segment),]
            rating <- rated_segment[[column]]
            if (!is.null(rating)) {
                if (is.factor(rating)) {
                    value <- as.integer(levels(rating)[rating])
                } else if (is.integer(rating)) {
                    value <- rating
                } else if (is.logical(rating)) {
                    value <- rating
                } else {
                }
                results_matrix[as.character(rater), as.character(segment)] <- value 
            }
        }
    }
    complete_results_matrix <- subset(results_matrix, select=full_data_segments)
    return(complete_results_matrix)
}

pairwise_percent_agree <- function(ratings) {
    ratings <- as.matrix(na.omit(ratings))
    ns <- nrow(ratings)
    nr <- ncol(ratings)
    total = 0
    agree = 0
    for (row in 1:ns) {
        for (i in 1:(nr-1)) {
            for (j in (i+1):nr) {
                total <- total + 1
                if (ratings[row,i] == ratings[row,j]) {
                    agree <- agree + 1
                }
            }
        }
    }
    return (1.0*agree/total);
}

compute_kappas_for_dataset <- function(dataset, columns_to_skip) {
    non_impediments <- grep('impediment', names(dataset), value=TRUE, invert=TRUE)
    agreement_matrix <- matrix(ncol=3, nrow=length(non_impediments), dimnames=list(non_impediments, c('fleiss\'s kappa', 'kappa SE', 'percent_agree')))
    for (column_name in non_impediments) {
        results_matrix <- construct_results_matrix(dataset, column_name)
        if (!(column_name %in% columns_to_skip)) {
        	kappa_results = kappam.fleiss(t(results_matrix))
            fleiss_kappa <- kappa_results$value
            fleiss_stderr <- (kappa_results$value)/(kappa_results$statistic) 
            percent_agree <- pairwise_percent_agree(t(results_matrix))
            print(paste(column_name, 'fleiss_kappa', fleiss_kappa, 'percent_agree', percent_agree))
            agreement_matrix[column_name, 'fleiss\'s kappa'] <- fleiss_kappa
            agreement_matrix[column_name, 'kappa SE'] <- fleiss_stderr
            agreement_matrix[column_name, 'percent_agree'] <- percent_agree
        }
    }
    return(agreement_matrix)
}

compute_pairwise_kappas_for_dataset <- function(dataset, raters, columns_to_skip) {
    if (length(raters) < 2) { stop("need at least two raters") }
    non_impediments <- grep('impediment', names(dataset), value=TRUE, invert=TRUE)
    pairs = (length(raters) * (length(raters)-1))/2
    columns = c()
    for (i in 2:length(raters)) {
        for (j in 1:(i-1)) {
            columns = c(columns, paste(i, j, sep=','), paste(i, ',', j, '-pi', sep=''))
        }
    }
    agreement_matrix <- matrix(ncol=pairs*2 + 1, nrow=length(non_impediments), dimnames=list(non_impediments, c(columns, 'percent_agree')))
    for (column_name in non_impediments) {
        if (!(column_name %in% columns_to_skip)) {
            for (i in 2:length(raters)) {
                for (j in 1:(i-1)) {
                    rater_subset = c(raters[i], raters[j])
                    subset <- dataset[which(dataset$User %in% rater_subset),]
                    results_matrix <- construct_results_matrix(subset, column_name)
                    if (diff(range(results_matrix)) == 0) {
                        # No variation -- consider Kappa to be 1.0, PI to be 0
                        kappa_for_subset <- 1.0
                        prevalence_index <- 0.0
                    } else {
                        kappa_for_subset <- kappa2(t(results_matrix))$value
                        prevalence_index <- compute_prevalence_index(t(results_matrix))
                    }
                    rater_column <- paste(i, j, sep=',')
                    agreement_matrix[column_name, rater_column] <- kappa_for_subset
                    print(paste(column_name, rater_column, kappa_for_subset))
                    agreement_matrix[column_name, paste(rater_column, '-pi', sep='')] <- prevalence_index
                    print(paste(column_name, rater_column, 'prevalence_index', prevalence_index))
                }
            }
            results_matrix <- construct_results_matrix(dataset, column_name)
            percent_agree <- pairwise_percent_agree(t(results_matrix))
            agreement_matrix[column_name, 'percent_agree'] <- percent_agree
            print(paste(column_name, 'percent_agree', percent_agree))
        }
    }
    return(agreement_matrix)
}

compute_frequency_table <- function(results_matrix) {
    ns <- nrow(results_matrix)
    nr <- ncol(results_matrix)
    
    r1 <- results_matrix[,1]; r2 <- results_matrix[,2]
    
    if (!is.factor(r1)) r1 <- factor(r1)
    if (!is.factor(r2)) r2 <- factor(r2)
    
    # Find factor levels
    if (length(levels(r1)) >= length(levels(r2))) {
        lev <- c(levels(r1), levels(r2))
    } else { 
        lev <- c(levels(r2), levels(r1))
    }
    
    lev <- lev[!duplicated(lev)]
    r1 <- factor(results_matrix[,1],levels=lev)
    r2 <- factor(results_matrix[,2],levels=lev)
    
    # Compute table
    ttab <- table(r1, r2)
}

compute_prevalence_index <- function(results_matrix) {
    ttab <- compute_frequency_table(results_matrix)

    # Find max along diagnonal, then compute mean prevalence of other values.
    max_prevalence <- max(diag(ttab))
    max_prev_index <- match(max_prevalence, diag(ttab))
    remaining_prevalences <- diag(ttab)[-max_prev_index]
    prevalence_proportions = (remaining_prevalences/(remaining_prevalences +max_prevalence))
    return (mean(prevalence_proportions))
}

compute_overall_average_prevalence <- function(dataset, column_name) {
    vals <- unique(dataset[,column_name])
    prevalences <- matrix(ncol=1, nrow=length(vals), dimnames=list(as.list(as.character(vals)),"count"))
    for (val in vals) {
        count = nrow(dataset[which(dataset[as.character(column_name)] == val),])
        prevalences[as.character(val),'count'] = count
    }
    max_prevalence = max(prevalences) * 1.0
    remaining_prevalences = prevalences[which(prevalences[,'count'] != max_prevalence),'count']
    prevalence_proportions = (remaining_prevalences/(remaining_prevalences +max_prevalence))
    return(mean(prevalence_proportions))
}

compute_correlations_for_dataset <- function(dataset, columns_to_use) {
    agreement_matrix <- matrix(ncol=1, nrow=length(columns_to_use), dimnames=list(columns_to_use, c('average_pearson_correlation')))
    for (column_name in columns_to_use) {
        results_matrix <- construct_results_matrix(dataset, column_name)
        pearson_cor <- compute_pearson(t(results_matrix))
        agreement_matrix[column_name, 'average_pearson_correlation'] <- pearson_cor
        print(paste(column_name, 'average correlation', pearson_cor))
    }
    return(agreement_matrix)
}

compute_pearson <- function(matrix) {
    correlation_matrix <- cor(matrix)
    rater_count <- nrow(correlation_matrix)
    total_correlations <- 0
    correlation_sum <- 0
    for (i in 2:rater_count) {
        for (j in 1:(i - 1)) {
            total_correlations <- total_correlations + 1
            correlation_sum <- correlation_sum + correlation_matrix[i,j]
        }
    }
    return (correlation_sum * 1.0/total_correlations)
}
                

continuous_ratings <- c(
        "Meta.1",
        "Meta.2",
        "MIUDQ.3",
        "MIUDQ.10",
        "MIUDQ.12",
        "MIUDQ.19",
        "MIUDQ.21"
)

metadata_columns <- c(
        "User",
        "Segment",
        "Meta.7",
        "Meta_time",
        "First._time",
        "Road_time",
        "Bike_time",
        "Sidewalk_time",
        "Other_time",
        "Land_time",
        "Appearance_time"
)

columns_to_skip <- c(continuous_ratings, metadata_columns)

kappas <- compute_kappas_for_dataset(full_data, columns_to_skip)
write.csv(kappas, "~/Projects/stats/150_block_pilot_kappas.csv")

kappas <- compute_pairwise_kappas_for_dataset(full_data, raters, columns_to_skip)
write.csv(kappas, "~/Projects/stats/150_block_pilot_pairwise_kappas.csv")


correlations <- compute_correlations_for_dataset(full_data, continuous_ratings)
write.csv(correlations, "~/Projects/stats/150_block_pilot_correlations.csv")

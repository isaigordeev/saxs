package main

import (
	"context"
	"log"
	"os"

	"github.com/jackc/pgx/v5"
	"saxs/producer/pkg/stream"
	"saxs/producer/pkg/transport"
	"saxs/producer/pkg/types"
)

func main() {
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		dbURL = "postgres://postgres:postgres@localhost:5433/saxs?sslmode=disable"
	}

	ctx := context.Background()
	conn, err := pgx.Connect(ctx, dbURL)
	if err != nil {
		log.Fatalf("Unable to connect to database: %v", err)
	}
	defer conn.Close(ctx)

	// Stream samples from PostgreSQL
	samples, errs := stream.Stream(ctx, conn)

	// Write to stdout (pipe is created by parent Python process)
	writer := transport.NewWriter(os.Stdout)

	for sample := range samples {
		flow := &types.FlowMetadata{
			Sample: sample.ID,
		}

		if _, err := writer.WriteCombined(&sample, flow); err != nil {
			log.Fatalf("Write failed: %v", err)
		}
	}

	// Check for any streaming errors
	if err := <-errs; err != nil {
		log.Fatalf("Stream error: %v", err)
	}
}


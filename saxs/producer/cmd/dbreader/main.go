package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/jackc/pgx/v5"
)

type SAXSData struct {
	ID        int64
	Q         float64
	Intensity float64
	Error     float64
}

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

	rows, err := conn.Query(ctx, "SELECT id, q, intensity, error FROM saxs_data LIMIT 10")
	if err != nil {
		log.Fatalf("Query failed: %v", err)
	}
	defer rows.Close()

	fmt.Println("SAXS Data (first 10 rows):")
	fmt.Println("---------------------------")

	for rows.Next() {
		var d SAXSData
		err := rows.Scan(&d.ID, &d.Q, &d.Intensity, &d.Error)
		if err != nil {
			log.Fatalf("Scan failed: %v", err)
		}
		fmt.Printf("id=%d q=%.6f I=%.4f err=%.4f\n", d.ID, d.Q, d.Intensity, d.Error)
	}

	if err := rows.Err(); err != nil {
		log.Fatalf("Rows error: %v", err)
	}

	// Count total
	var count int64
	err = conn.QueryRow(ctx, "SELECT COUNT(*) FROM saxs_data").Scan(&count)
	if err != nil {
		log.Fatalf("Count failed: %v", err)
	}
	fmt.Printf("\nTotal rows: %d\n", count)
}

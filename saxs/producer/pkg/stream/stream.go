package stream

import (
	"context"

	"github.com/jackc/pgx/v5"
)

type SAXSSample struct {
	ID  string
	Q   []float64
	I   []float64
	Err []float64
}

func stream(ctx context.Context, conn *pgx.Conn) (<-chan SAXSSample, <-chan error) {
	out := make(chan SAXSSample)
	errors := make(chan error, 1)

	go func() {
		defer close(out)

		rows, err := conn.Query(ctx, "SELECT id, q, intensity FROM saxs_data ORDER BY id, q")

		if err != nil {
			errors <- err
			close(errors)
			return
		}
		defer rows.Close()

		for rows.Next() {
			var id string
			var q, intensity, e float64

			if err := rows.Scan(&id, &q, &intensity, &e); err != nil {
				errors <- err
				return
			}

			var sample = SAXSSample{ID: id}

			sample.Q = append(sample.Q, q)
			sample.I = append(sample.I, intensity)
			sample.Q = append(sample.Err, e)

			out <- sample

		}

		if err := rows.Err(); err != nil {
			errors <- err
		}
		close(errors)

	}()

	return out, errors
}

-- db_sql/04_functions.sql
-- Assign a room to a class with conflict check (simple version).

CREATE OR REPLACE FUNCTION assign_room(p_class_id BIGINT, p_room_id BIGINT)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE
  v_term_id BIGINT;
  v_days SMALLINT[];
  v_start INT;
  v_end INT;
  v_conflict BIGINT;
BEGIN
  SELECT term_id, days_int, start_min, end_min INTO v_term_id, v_days, v_start, v_end
  FROM classes WHERE id = p_class_id;
  IF v_term_id IS NULL THEN
    RAISE EXCEPTION 'Class not found';
  END IF;
  IF v_days IS NULL OR v_start IS NULL OR v_end IS NULL THEN
    RAISE EXCEPTION 'Class schedule is incomplete (use numeric schedule fields)';
  END IF;

  -- conflict: same term, same room, overlap in time and day
  SELECT c.id INTO v_conflict
  FROM classes c
  WHERE c.id <> p_class_id
    AND c.term_id = v_term_id
    AND c.room_id = p_room_id
    AND EXISTS (SELECT 1 FROM unnest(c.days_int) d WHERE d = ANY (v_days))
    AND c.start_min < v_end AND c.end_min > v_start
  LIMIT 1;

  IF v_conflict IS NOT NULL THEN
    RAISE EXCEPTION 'Room conflict at that time';
  END IF;

  UPDATE classes SET room_id = p_room_id WHERE id = p_class_id;
END;
$$;

-- For strongest DB-level guarantees, consider modeling each meeting row
-- and using a GiST exclusion constraint on (room_id, day, time_range).

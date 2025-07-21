import { useLayoutEffect, useRef } from 'react';

/**
 * Custom hook to synchronize the height of two columns.
 * The right column will automatically match the height of the left column on desktop screens.
 * On mobile screens, both columns use their natural height.
 * 
 * Uses ResizeObserver for efficient height tracking and useLayoutEffect to prevent visual flicker.
 * The lg:self-start CSS class prevents flexbox circular dependencies.
 */
export function useMatchHeight() {
  const leftRef = useRef(null);
  const rightRef = useRef(null);

  useLayoutEffect(() => {
    const left = leftRef.current;
    const right = rightRef.current;
    if (!left || !right) return;

    const desktop = () =>
      window.matchMedia('(min-width:1024px)').matches;

    const sync = () => {
      if (!desktop()) {
        right.style.height = '';         // mobile → natural height
        return;
      }
      const h = left.offsetHeight;
      if (h > 0) right.style.height = h + 'px';   // ignore 0‑px stubs
    };

    // 1  watch the left column
    const ro = new ResizeObserver(sync);
    ro.observe(left);                                    // initial fire is automatic

    // 2  watch viewport/break‑point changes
    window.addEventListener('resize', sync);

    return () => {
      ro.disconnect();
      window.removeEventListener('resize', sync);
    };
  }, []);

  return { leftRef, rightRef };
}

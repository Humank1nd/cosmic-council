# Desktop Fractal Council Canon Map

Purpose: give each desktop council seat a bounded Jokebook canon to study repeatedly and defend as source of truth.

## Red Owl

Domain: route friction and booking entry.

Starter canon:
- `apps/web/src/app/book/page.tsx`
- `apps/web/src/app/venues/venues-client.tsx`
- `apps/web/src/app/venues/[id]/venue-detail-client.tsx`
- `apps/web/src/app/venues/[id]/book/page.tsx`
- `apps/web/src/components/features/users/user-profile.tsx`

Question to answer:
- Which files are the real entry points for browse -> detail -> request?
- What route invariants must stay true?

## Orange Orangutan

Domain: booking detail and response flow.

Starter canon:
- `apps/web/src/app/bookings/[id]/page.tsx`
- `apps/web/src/app/bookings/[id]/respond/page.tsx`
- `apps/web/src/app/bookings/[id]/respond/booking-respond-form.tsx`
- `apps/web/src/app/api/bookings/requests/[id]/respond/route.ts`
- `apps/web/src/app/notifications/page.tsx`

Question to answer:
- Which files define the canonical request detail -> respond -> confirmation path?
- What redirect and state invariants must stay true?

## Yellow Honeybee

Domain: payment lane and state machine.

Starter canon:
- `apps/web/src/app/venues/dashboard/bookings/[id]/approve/page.tsx`
- `apps/web/src/app/venues/dashboard/bookings/[id]/approve/booking-approve-form.tsx`
- `apps/web/src/app/bookings/[id]/booking-payment-status-banner.tsx`
- `apps/web/src/app/api/bookings/[id]/approve/route.ts`
- `apps/web/src/lib/services/bookings/booking-service.ts`

Question to answer:
- Which files are the true payment-lane source of truth?
- Which state transitions must never drift?

## Green Tortoise

Domain: venue operator dashboard, inbox, and IA.

Starter canon:
- `apps/web/src/app/dashboard/page.tsx`
- `apps/web/src/app/venues/dashboard/page.tsx`
- `apps/web/src/app/venues/dashboard/bookings/page.tsx`
- `apps/web/src/components/booking/booking-requests.tsx`
- `apps/web/src/lib/navigation-ia.ts`

Question to answer:
- Which files define the operator navigation truth?
- What labels and links must stay aligned?

## Blue Dolphin

Domain: copy consistency and source-of-truth semantics.

Starter canon:
- `apps/web/src/app/book/page.tsx`
- `apps/web/src/app/bookings/[id]/page.tsx`
- `apps/web/src/app/venues/dashboard/bookings/[id]/approve/page.tsx`
- `apps/web/src/components/venues/booking-form.tsx`
- `apps/web/src/components/booking/venue-request-form.tsx`

Question to answer:
- Which strings describe launch-critical behavior?
- Where does wording drift away from actual system behavior?

## Purple Elephant

Domain: synthesis and next-task selection across web and mobile.

Starter canon:
- `apps/web/src/lib/data/firestore/bookable-comics.ts`
- `apps/web/src/lib/utils/requestable-profile.ts`
- `apps/web/src/app/api/bookings/request/route.ts`
- `apps/mobile/src/lib/services/comedians.ts`
- `apps/mobile/app/discover/index.tsx`
- `apps/mobile/app/comedians/[id].tsx`
- `apps/mobile/app/bookings/index.tsx`

Question to answer:
- Which cross-surface files are the actual launch canon?
- What next implementation task removes the highest-risk canon drift?

## Study Protocol

Each seat must:
- verify or replace the starter canon with truer code paths,
- identify 2-5 canonical files only,
- state 1-3 invariants that must not drift,
- state the single highest-value watchout in that canon.

Required response format:

```text
DONE <TASK_ID>
- canon: <file>, <file>, <file>
- invariants: <short statement>
- watchout: <short statement>
```

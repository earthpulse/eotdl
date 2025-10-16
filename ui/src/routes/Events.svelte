<script>
  import events from "./events.json";

  import { parseISO, compareAsc } from "date-fns";

  let currentDate = $state(new Date());
  let currentMonth = $derived(currentDate.getMonth());
  let currentYear = $derived(currentDate.getFullYear());

  function getDaysInMonth(month, year) {
    return new Date(year, month + 1, 0).getDate();
  }

  function getFirstDayOfMonth(month, year) {
    return (new Date(year, month, 1).getDay() + 6) % 7; // Adjust to start from Monday
  }

  function generateCalendar(month, year) {
    const daysInMonth = getDaysInMonth(month, year);
    const firstDay = getFirstDayOfMonth(month, year);
    const calendar = [];

    let day = 1;
    for (let i = 0; i < 6; i++) {
      const week = [];
      for (let j = 0; j < 7; j++) {
        if (i === 0 && j < firstDay) {
          week.push(null);
        } else if (day > daysInMonth) {
          week.push(null);
        } else {
          week.push(day);
          day++;
        }
      }
      calendar.push(week);
      if (day > daysInMonth) break;
    }

    return calendar;
  }

  function hasDayEvent(day) {
    const dateString = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    return events.some(
      (event) => event.date === dateString || event.dateTo === dateString,
    );
  }

  function hasEvent(day) {
    const dateString = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    return events.some(
      (event) =>
        event.dateTo >= dateString &&
        event.date <= dateString &&
        event.dateTo > event.date,
    );
  }

  function getEvent(day) {
    const dateString = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    let eventsOnDay = [];
    events
      .filter(
        (event) =>
          event.dateTo >= dateString &&
          event.date <= dateString &&
          event.dateTo > event.date,
      )
      .forEach((event) => {
        eventsOnDay.push(event.title);
      });
    return eventsOnDay.join(", ");
  }

  function prevMonth() {
    currentDate = new Date(currentYear, currentMonth - 1, 1);
  }

  function nextMonth() {
    currentDate = new Date(currentYear, currentMonth + 1, 1);
  }

  let calendarDays = $derived(generateCalendar(currentMonth, currentYear));

  let sortedEvents = $derived(
    events.sort((a, b) => compareAsc(parseISO(a.dateTo), parseISO(b.dateTo))),
  );

  let filteredEvents = $derived(
    sortedEvents.filter(
      (event) =>
        new Date(event.dateTo || event.date) >=
        new Date(new Date().setDate(new Date().getDate() - 1)),
    ),
  );

  let limit = $state(3);
  let shownEvents = $derived(
    filteredEvents.slice(0, limit).sort(function (a, b) {
      if (a.date > b.date) {
        return 1;
      } else if (a.date < b.date) {
        return -1;
      }
      return 0;
    }),
  );

  let showMore = $state(-1);
</script>

<div class="w-full flex flex-col gap-3">
  <h2
    class="font-bold text-3xl w-full text-left pb-6 text-[rgb(74,191,167)] uppercase"
  >
    Events
  </h2>
  <div class="max-w-sm mx-auto w-full">
    <div class="flex justify-between items-center mb-4">
      <button class="text-md text-[rgb(74,191,167)]" onclick={prevMonth}
        >&lt;</button
      >
      <h2 class="text-md">
        {new Date(currentYear, currentMonth).toLocaleString("en", {
          month: "long",
          year: "numeric",
        })}
      </h2>
      <button class="text-md text-[rgb(74,191,167)]" onclick={nextMonth}
        >&gt;</button
      >
    </div>
    <table class="w-full border-collapse text-sm text-slate-400">
      <thead>
        <tr class="text-xs">
          <th class="text-center">Mon</th>
          <th class="text-center">Tue</th>
          <th class="text-center">Wed</th>
          <th class="text-center">Thu</th>
          <th class="text-center">Fri</th>
          <th class="text-center">Sat</th>
          <th class="text-center">Sun</th>
        </tr>
      </thead>
      <tbody>
        {#each calendarDays as week}
          <tr>
            {#each week as day}
              {#if day && hasDayEvent(day)}
                <td
                  class="
									{hasEvent(day - 1) && hasEvent(day + 1)
                    ? ''
                    : hasEvent(day - 1)
                      ? 'rounded-r-xl'
                      : hasEvent(day + 1)
                        ? 'rounded-l-xl'
                        : 'rounded-full'} 
									text-center p-1 font-bold text-black bg-[rgb(74,191,167)]"
                >
                  <p class="tooltip" data-tip={getEvent(day)}>{day}</p>
                </td>
              {:else if day && hasEvent(day)}
                <td
                  class="text-center p-1 font-bold text-black bg-[rgb(74,191,167)]"
                >
                  {day}
                </td>
              {:else if day === new Date().getDate() && currentMonth === new Date().getMonth() && currentYear === new Date().getFullYear()}
                <td
                  class="text-center p-1 rounded-full font-bold text-black bg-gray-200"
                >
                  {day}
                </td>
              {:else}
                <td class="text-center p-1">{day || ""}</td>
              {/if}
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
  {#if events.length == 0}
    <p class="text-center text-gray-500">No events found</p>
  {/if}
  <ul class="flex flex-col gap-2 h-96 overflow-y-auto scrollbar-hide">
    {#each shownEvents as event, ix}
      <li class="mb-4">
        <h3 class="text-md font-bold">{event.title}</h3>
        {#if !event.dateTo}
          <p class="text-xs text-gray-500">
            {new Date(event.date).toLocaleDateString("en-US", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </p>
        {:else}
          <p class="text-xs text-gray-500">
            {new Date(event.date).toLocaleDateString("en-US", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
            to
            {new Date(event.dateTo).toLocaleDateString("en-US", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </p>
        {/if}
        {#if showMore === ix}
          <p class="text-gray-600 text-xs">{event.description}</p>
        {:else}
          <p class="text-gray-600 text-xs line-clamp-3">
            {event.description}
          </p>
        {/if}
        <span class="flex flex-row justify-between mt-2">
          {#if showMore === ix}
            <button
              onclick={() => (showMore = -1)}
              class="text-xs text-[rgb(74,191,167)]">Show less</button
            >
          {:else}
            <button
              onclick={() => (showMore = ix)}
              class="text-xs text-[rgb(74,191,167)]">Show more</button
            >
          {/if}
          <a
            href={event.link}
            target="_blank"
            rel="noopener noreferrer"
            class="text-[rgb(74,191,167)] hover:underline text-xs">More Info</a
          >
        </span>
        <hr class="my-2 border-t border-[rgb(74,191,167)]" />
      </li>
    {/each}
    <button
      onclick={() => (limit += 3)}
      class="text-xs text-[rgb(74,191,167)] cursor-pointer"
      >Show more events</button
    >
  </ul>
</div>

<style>
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }

  /* For IE, Edge and Firefox */
  .scrollbar-hide {
    -ms-overflow-style: none; /* IE and Edge */
    scrollbar-width: none; /* Firefox */
  }
</style>

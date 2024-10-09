<script>
	import events from "./events.json";

	// Example event:
	// {
	// 	"title": "Event 1",
	// 	"description": "Description 1",
	// 	"date": "2024-09-05",
	// 	"link": "https://www.google.com"
	// }

	let currentDate = new Date();
	let currentMonth;
	let currentYear;

	$: {
		currentMonth = currentDate.getMonth();
		currentYear = currentDate.getFullYear();
	}

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
		const currentDateString = new Date().toISOString().split("T")[0];
		return events.some(
			(event) =>
				(event.date === dateString || event.dateTo === dateString) &&
				event.date >= currentDateString,
		);
	}
	function hasEvent(day) {
		const dateString = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
		const currentDateString = new Date().toISOString().split("T")[0];
		return events.some(
			(event) =>
				event.dateTo >= dateString &&
				event.date <= dateString &&
				event.dateTo > event.date &&
				event.date >= currentDateString,
		);
	}

	function prevMonth() {
		currentDate = new Date(currentYear, currentMonth - 1, 1);
	}

	function nextMonth() {
		currentDate = new Date(currentYear, currentMonth + 1, 1);
	}

	$: calendarDays = generateCalendar(currentMonth, currentYear);
</script>

<div class="w-full flex flex-col gap-3">
	<h2
		class="font-bold text-3xl w-full text-left pb-6 text-[rgb(74,191,167)] uppercase"
	>
		Events
	</h2>
	<div class="max-w-sm mx-auto w-full">
		<div class="flex justify-between items-center mb-4">
			<button class="text-md text-[rgb(74,191,167)]" on:click={prevMonth}
				>&lt;</button
			>
			<h2 class="text-md">
				{new Date(currentYear, currentMonth).toLocaleString("en", {
					month: "long",
					year: "numeric",
				})}
			</h2>
			<button class="text-md text-[rgb(74,191,167)]" on:click={nextMonth}
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
									{day}
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
	<ul class="flex flex-col gap-2">
		{#each events.filter((event) => new Date(event.date) >= new Date(new Date().setDate(new Date().getDate() - 1))) as event}
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
				<p class="text-gray-600 text-xs">{event.description}</p>
				<a
					href={event.link}
					target="_blank"
					rel="noopener noreferrer"
					class="text-[rgb(74,191,167)] hover:underline text-xs"
					>More Info</a
				>
				<hr class="my-2 border-t border-[rgb(74,191,167)]" />
			</li>
		{/each}
	</ul>
</div>

<script>
    import { page } from "$app/stores";
    import auth from "$stores/auth.svelte";
</script>

<div class="w-full flex flex-col items-center sm:px-14 px-3 min-h-screen max-w-5xl m-auto">
    <div class="flex gap-4">
        <div class="flex flex-col items-center w-60 text-center">
            <img src="/gamification/gold_coin_pile.png" alt="logo" class="w-30" />
            <h1 class="text-4xl font-bold">{auth.user.credits}</h1>
            <h1 class="text-xl font-bold">Credits</h1>
            <p>
                Credits are used to purchase  . . .
            </p>
        </div>
        <div class="h-[full] w-1 border-r border-gray-300"></div>
        <div class="flex flex-col items-center w-60 text-center">
            <img src="/gamification/silver_coin_pile.png" alt="logo" class="w-30" />
            <h1 class="text-4xl font-bold">{auth.user.pseudocredits}</h1>
            <h1 class="text-xl font-bold">Pseudocredits</h1>
            <p>
                Pseudocredits can be converted to credits
            </p>
        </div>
    </div>
    <div class="flex flex-col items-center mt-10">
        <a class="btn btn-outline" href="mailto:it@earthpulse.ai?subject=Pseudocredits%20to%20credits&body=I%20want%20to%20convert%20my%20pseudocredits%20to%20credits.">
            Convert Pseudocredits to Credits
        </a>
    </div>
</div>
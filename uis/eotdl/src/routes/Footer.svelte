<script>
    import Twitter from "svelte-material-icons/Twitter.svelte";
    import Youtube from "svelte-material-icons/Youtube.svelte";
    import Linkedin from "svelte-material-icons/Linkedin.svelte";
</script>

<footer class="footer p-10 bg-blue-500 flex flex-row justify-between">
    <ul class="text-green-200">
        <li><a href="/" class="hover:underline">Privacy Policy</a></li>
        <li><a href="/" class="hover:underline">Terms & Conditions</a></li>
        <li><a href="/" class="hover:underline">Cookies</a></li>
    </ul>
    <div class="text-slate-100">
        <p>
            EOTDL is carried out under a programme of, and funded by the
            European Space Agency (ESA).
        </p>
        <p>
            Disclaimer: The views expressed on this site shall not be construed
            to reflect the official opinion of ESA.
        </p>
    </div>
    <div class="flex flex-row text-green-200 gap-10 font-bold text-lg">
        <div class="flex flex-col">
            <h2 class="opacity-30">Contact Us</h2>
            <a
                href="/"
                class="border border-green-200 rounded-md p-1 text-center opacity-30 hover:opacity-100 mt-2"
                >Contact</a
            >
        </div>
        <div class="flex flex-col">
            <h2 class="opacity-30">Follow Us</h2>
            <div class="flex flex-row gap-2 text-2xl pt-3">
                <a href="/" class="opacity-30 hover:opacity-100"><Twitter /></a>
                <a href="/" class="opacity-30 hover:opacity-100"><Youtube /></a>
                <a href="/" class="opacity-30 hover:opacity-100"><Linkedin /></a
                >
            </div>
        </div>
    </div>
</footer>

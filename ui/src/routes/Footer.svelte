<script>
    import Twitter from "svelte-material-icons/Twitter.svelte";
    import Discord from "svelte-material-icons/Discord.svelte";
    import Linkedin from "svelte-material-icons/Linkedin.svelte";
</script>

<footer
    class="footer p-10 bg-blue-500 flex flex-col md:flex-row justify-between"
>
    <ul class="text-[#335e6f]">
        <li>
            <a href="/PrivacyPolicy.pdf" class="hover:underline" target="_blank"
                >Privacy Policy</a
            >
        </li>
        <li>
            <a
                href="/TermsConditions.pdf"
                class="hover:underline"
                target="_blank">Terms & Conditions</a
            >
        </li>
        <li>
            <a href="/cookies" class="hover:underline" target="_blank"
                >Cookies</a
            >
        </li>
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
    <div class="flex flex-row text-[#335e6f] gap-10 font-bold text-lg">
        <div class="flex flex-col">
            <h2>Contact Us</h2>
            <a
                href="mailto:support@eotdl.com"
                class="border border-[#335e6f] rounded-md p-1 text-center hover:text-green-200 hover:border-green-200 mt-2"
                >Contact</a
            >
        </div>
        <div class="flex flex-col">
            <h2>Follow Us</h2>
            <div class="flex flex-row gap-2 text-2xl pt-3">
                <a
                    href="https://twitter.com/eotdl"
                    target="_blank"
                    class="hover:text-green-200"><Twitter /></a
                >
                <a
                    href="https://discord.gg/hYxc5AJB92"
                    target="_blank"
                    class="hover:text-green-200"><Discord /></a
                >
                <a
                    href="https://www.linkedin.com/company/eotdl"
                    target="_blank"
                    class="hover:text-green-200"><Linkedin /></a
                >
            </div>
        </div>
    </div>
</footer>

<style>
    footer {
        border-top: 4px solid #335e6f;
    }
</style>

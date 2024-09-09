<script>
  import "../app.css";
  import { Navbar, NavBrand, NavLi, NavUl, NavHamburger, Dropdown, DropdownItem, Avatar, Button } from 'flowbite-svelte';
  import { page } from '$app/stores';
  import { UserCircle } from 'svelte-heros-v2';

  let navItems = [
    { name: 'Home', href: '/web/' },
    // Additional items can be added by child pages
  ];
  // Placeholder user data (replace with actual user management logic)
  let user = {
    name: 'John Doe',
    email: 'john@example.com',
    avatar: 'https://flowbite.com/docs/images/people/profile-picture-5.jpg'
  };

  function handleSignOut() {
    // Implement sign out logic here
    console.log('User signed out');
  }
</script>

<div class="w-full">
  <Navbar let:hidden let:toggle class="w-full">
    <NavBrand href="/">
      <span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white">Rhetoria</span>
    </NavBrand>
    <NavHamburger on:click={toggle} />
    <NavUl {hidden}>
      {#each navItems as item}
        <NavLi href={item.href} active={$page.url.pathname === item.href}>{item.name}</NavLi>
      {/each}
    </NavUl>
    <div class="flex items-center ml-auto justify-end">
      <Dropdown class="w-48">
        <Button class="!p-0" slot="trigger">
          <UserCircle class="w-8 h-8 text-gray-500 dark:text-gray-400" solid />
        </Button>
        <div class="px-4 py-3">
          <span class="block text-sm text-gray-900 dark:text-white">{user.name}</span>
          <span class="block text-sm font-medium text-gray-500 truncate dark:text-gray-400">{user.email}</span>
        </div>
        <DropdownItem href="/web/profile">Profile</DropdownItem>
        <DropdownItem href="/web/account">Account Settings</DropdownItem>
        <DropdownItem on:click={handleSignOut}>Sign out</DropdownItem>
      </Dropdown>
    </div>
  </Navbar>
</div>

<main>
  <slot />
</main>
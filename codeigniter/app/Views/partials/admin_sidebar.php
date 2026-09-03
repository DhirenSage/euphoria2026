<?php $sidebarRoles=session('roles')??[]; $canManageEvents=(bool)array_intersect($sidebarRoles,['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN']); $canManageMedia=(bool)array_intersect($sidebarRoles,['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN','CONTENT_MANAGER']); $canViewPayments=(bool)array_intersect($sidebarRoles,['SUPER_ADMIN','PROGRAMME_ADMIN','FINANCE']); $canViewEntry=(bool)array_intersect($sidebarRoles,['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN','REPORT_VIEWER']); ?>
<aside class="admin-sidebar" data-testid="admin-sidebar">
  <a class="brand" href="<?= base_url('admin') ?>" data-testid="admin-brand-link"><span class="brand-mark">S</span><span>EUPHORIA <strong>OPS</strong></span></a>
  <nav class="admin-nav" data-testid="admin-navigation">
    <span class="eyebrow">COMMAND</span>
    <a class="<?= ($active ?? '')==='dashboard'?'admin-nav-active':'' ?>" href="<?= base_url('admin') ?>" data-testid="admin-nav-dashboard">Overview</a>
    <a class="<?= ($active ?? '')==='categories'?'admin-nav-active':'' ?>" href="<?= base_url('admin/categories') ?>" data-testid="admin-nav-categories">Categories</a>
    <a class="<?= ($active ?? '')==='events'?'admin-nav-active':'' ?>" href="<?= base_url('admin/events') ?>" data-testid="admin-nav-events">Events</a>
    <?php if($canManageMedia): ?><a class="<?= ($active ?? '')==='media'?'admin-nav-active':'' ?>" href="<?= base_url('admin/media') ?>" data-testid="admin-nav-media">Gallery & video</a><?php endif ?>
    <a class="<?= ($active ?? '')==='registrations'?'admin-nav-active':'' ?>" href="<?= base_url('admin/registrations') ?>" data-testid="admin-nav-registrations">Participants</a>
    <a class="<?= ($active ?? '')==='attendance'?'admin-nav-active':'' ?>" href="<?= base_url('admin/attendance') ?>" data-testid="admin-nav-attendance">Attendance</a>
    <?php if($canManageEvents): ?><a class="<?= ($active ?? '')==='bulk-passes'?'admin-nav-active':'' ?>" href="<?= base_url('admin/bulk-passes') ?>" data-testid="admin-nav-bulk-passes">Bulk passes</a><?php endif ?>
    <?php if(in_array('SUPER_ADMIN',$sidebarRoles,true)): ?><a class="<?= ($active ?? '')==='scanners'?'admin-nav-active':'' ?>" href="<?= base_url('admin/scanners') ?>" data-testid="admin-nav-scanners">Scanner users</a><?php endif ?>
    <?php if($canViewPayments): ?><a class="<?= ($active ?? '')==='payments'?'admin-nav-active':'' ?>" href="<?= base_url('admin/payments') ?>" data-testid="admin-nav-payments">Payments</a><?php endif ?>
    <?php if($canViewEntry): ?><a class="<?= ($active ?? '')==='entry-tracking'?'admin-nav-active':'' ?>" href="<?= base_url('admin/entry-tracking') ?>" data-testid="admin-nav-entry-tracking">Entry tracking</a><?php endif ?>
    <a class="<?= ($active ?? '')==='reports'?'admin-nav-active':'' ?>" href="<?= base_url('admin/reports') ?>" data-testid="admin-nav-reports">Reports</a>
    <span class="eyebrow nav-spacer">SYSTEM</span>
    <a class="<?= ($active ?? '')==='settings'?'admin-nav-active':'' ?>" href="<?= base_url('admin/settings') ?>" data-testid="admin-nav-settings">Settings</a>
    <a href="<?= base_url('scanner') ?>" data-testid="admin-nav-scanner">Scanner ↗</a>
  </nav>
  <form method="post" action="<?= base_url('logout') ?>" class="admin-logout-form"><input type="hidden" name="<?= csrf_token() ?>" value="<?= csrf_hash() ?>"><button type="submit" class="admin-logout" data-testid="admin-logout-link">Sign out</button></form>
</aside>
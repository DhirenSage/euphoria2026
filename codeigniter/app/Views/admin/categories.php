<main class="admin-shell">
  <?= view('partials/admin_sidebar',['active'=>'categories']) ?>
  <section class="admin-content">
    <div class="admin-topbar"><div><span class="eyebrow accent">PROGRAMME STRUCTURE</span><h1 data-testid="categories-page-title">Categories</h1></div><span class="mono" data-testid="category-count"><?= count($categories) ?> TOTAL</span></div>
    <div class="admin-split">
      <form method="post" action="<?= base_url('admin/categories') ?>" class="admin-panel admin-form" data-testid="category-create-form">
        <input type="hidden" name="<?= csrf_token() ?>" value="<?= csrf_hash() ?>">
        <div class="panel-heading"><div><span class="eyebrow">NEW CATEGORY</span><h2>Build a new track</h2></div></div>
        <label>Programme<select name="programme_id" required data-testid="category-programme-select"><?php foreach($programmes as $programme): ?><option value="<?= esc($programme['id']) ?>"><?= esc($programme['name']) ?></option><?php endforeach ?></select></label>
        <label>Name<input name="name" required data-testid="category-name-input"></label>
        <label>Slug<input name="slug" placeholder="auto-generated-from-name" data-testid="category-slug-input"></label>
        <label>Description<textarea name="description" rows="3" data-testid="category-description-input"></textarea></label>
        <div class="form-grid compact-grid"><label>Icon label<input name="icon" placeholder="Music" data-testid="category-icon-input"></label><label>Display order<input type="number" name="display_order" value="0" min="0" data-testid="category-order-input"></label></div>
        <label class="checkbox-label"><input type="checkbox" name="is_active" value="1" checked data-testid="category-active-checkbox"> Active on the public site</label>
        <button class="button button-yellow" type="submit" data-testid="category-create-button">Create category <span>↗</span></button>
      </form>
      <div class="admin-panel"><div class="panel-heading"><div><span class="eyebrow">CURRENT STRUCTURE</span><h2>Programme categories</h2></div></div>
        <div class="stack-list"><?php foreach($categories as $category): ?>
          <form method="post" action="<?= base_url('admin/categories/'.$category['id']) ?>" class="editable-row" data-testid="category-row-<?= esc($category['id']) ?>">
            <input type="hidden" name="<?= csrf_token() ?>" value="<?= csrf_hash() ?>"><input type="hidden" name="programme_id" value="<?= esc($category['programme_id']) ?>">
            <div class="editable-row-head"><strong data-testid="category-name-<?= esc($category['id']) ?>"><?= esc($category['name']) ?></strong><span class="status <?= $category['is_active']?'status-success':'status-warning' ?>"><?= $category['is_active']?'ACTIVE':'INACTIVE' ?> · <?= esc($category['event_count']) ?> EVENTS</span></div>
            <div class="form-grid compact-grid"><label>Name<input name="name" value="<?= esc($category['name']) ?>"></label><label>Slug<input name="slug" value="<?= esc($category['slug']) ?>"></label><label>Order<input type="number" name="display_order" value="<?= esc($category['display_order']) ?>"></label><label class="checkbox-label"><input type="checkbox" name="is_active" value="1" <?= $category['is_active']?'checked':'' ?>> Active</label></div>
            <label>Description<textarea name="description" rows="2"><?= esc($category['description']) ?></textarea></label><input type="hidden" name="icon" value="<?= esc($category['icon']??'') ?>">
            <div class="row-actions"><button class="table-action" type="submit" data-testid="category-save-<?= esc($category['id']) ?>">Save</button><button class="table-action danger-action" type="submit" formaction="<?= base_url('admin/categories/'.$category['id'].'/delete') ?>" data-confirm="Delete this empty category?" data-testid="category-delete-<?= esc($category['id']) ?>">Delete</button></div>
          </form>
        <?php endforeach ?></div>
      </div>
    </div>
  </section>
</main>